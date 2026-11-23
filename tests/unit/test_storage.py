from __future__ import annotations

import hashlib
import sqlite3
from io import BytesIO
from zipfile import ZipFile

import pytest
from openpyxl import Workbook

from crm_cloud_demo.apps.cloud import storage


def make_xlsx_bytes() -> bytes:
    workbook = Workbook()
    workbook.active.title = "Deals"
    workbook.active.append(["ID", "Amount"])
    workbook.active.append(["CRM-1001", 100.0])
    output = BytesIO()
    workbook.save(output)
    return output.getvalue()


@pytest.fixture
def isolated_storage(tmp_path, monkeypatch):
    from dataclasses import replace

    from crm_cloud_demo.config import settings

    test_settings = replace(
        settings,
        storage_path=tmp_path / "storage",
        database_path=tmp_path / "storage" / "metadata.db",
    )
    monkeypatch.setattr(storage, "settings", test_settings)
    storage.init_database()
    return test_settings


def test_safe_filename_removes_directories_and_unsupported_characters():
    assert storage._safe_filename(r"..\..\Quarterly report!.xlsx") == "Quarterly_report_.xlsx"


@pytest.mark.parametrize("filename", ["", ".", "..", "report.csv", "folder/", "bad\x00name.xlsx"])
def test_safe_filename_rejects_invalid_names(filename: str):
    with pytest.raises(storage.InvalidDocumentError):
        storage._safe_filename(filename)


def test_safe_filename_normalizes_extension_case():
    assert storage._safe_filename("REPORT.XLSX") == "REPORT.xlsx"


def test_validate_xlsx_accepts_a_real_workbook():
    storage._validate_xlsx(make_xlsx_bytes())


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (b"", "vazio"),
        (b"not an excel file", "estrutura XLSX"),
        (b"PK\x03\x04broken", "validar a planilha"),
    ],
)
def test_validate_xlsx_rejects_invalid_content(content: bytes, message: str):
    with pytest.raises(storage.InvalidDocumentError, match=message):
        storage._validate_xlsx(content)


def test_validate_xlsx_rejects_files_over_the_upload_limit():
    content = b"PK" + b"x" * storage.MAX_UPLOAD_BYTES
    with pytest.raises(storage.InvalidDocumentError, match="10 MB"):
        storage._validate_xlsx(content)


def test_validate_xlsx_rejects_zip_archives_without_workbook_parts():
    output = BytesIO()
    with ZipFile(output, "w") as archive:
        archive.writestr("readme.txt", "not an Excel workbook")

    with pytest.raises(storage.InvalidDocumentError, match="Estrutura de planilha"):
        storage._validate_xlsx(output.getvalue())


def test_validate_xlsx_rejects_archives_with_too_many_entries():
    output = BytesIO()
    with ZipFile(output, "w") as archive:
        for index in range(storage.MAX_ZIP_ENTRIES + 1):
            archive.writestr(f"entry-{index}.txt", "x")

    with pytest.raises(storage.InvalidDocumentError, match="conteúdo excessivo"):
        storage._validate_xlsx(output.getvalue())


def test_save_document_records_hash_and_increments_versions(isolated_storage):
    content = make_xlsx_bytes()

    first = storage.save_document("sales-report.xlsx", content)
    second = storage.save_document("sales-report.xlsx", content)

    assert first["version"] == 1
    assert second["version"] == 2
    assert first["id"] != second["id"]
    assert first["sha256"] == hashlib.sha256(content).hexdigest()
    assert first["size_bytes"] == len(content)

    upload_directory = isolated_storage.storage_path / "uploads"
    assert (upload_directory / first["stored_filename"]).is_file()
    assert (upload_directory / second["stored_filename"]).is_file()

    documents = storage.list_documents()
    assert len(documents) == 2
    assert {item["version"] for item in documents} == {1, 2}


def test_save_document_rejects_invalid_file_without_writing(isolated_storage):
    with pytest.raises(storage.InvalidDocumentError):
        storage.save_document("bad.xlsx", b"not an xlsx")

    assert storage.list_documents() == []
    upload_directory = isolated_storage.storage_path / "uploads"
    assert list(upload_directory.iterdir()) == []


def test_save_document_removes_file_when_database_insert_fails(
    isolated_storage,
    monkeypatch,
):
    real_connect = sqlite3.connect

    class FailingConnection:
        def __init__(self, connection):
            self._connection = connection

        def __getattr__(self, name):
            return getattr(self._connection, name)

        def __setattr__(self, name, value):
            if name == "_connection":
                object.__setattr__(self, name, value)
            else:
                setattr(self._connection, name, value)

        def execute(self, query, parameters=()):
            if "INSERT INTO uploads" in query:
                raise sqlite3.OperationalError("simulated metadata write failure")
            return self._connection.execute(query, parameters)

    monkeypatch.setattr(
        storage.sqlite3,
        "connect",
        lambda *args, **kwargs: FailingConnection(real_connect(*args, **kwargs)),
    )

    with pytest.raises(sqlite3.OperationalError, match="simulated"):
        storage.save_document("rollback.xlsx", make_xlsx_bytes())

    upload_directory = isolated_storage.storage_path / "uploads"
    assert list(upload_directory.iterdir()) == []
