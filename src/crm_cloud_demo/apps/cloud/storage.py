from __future__ import annotations

import hashlib
import re
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

from openpyxl import load_workbook

from crm_cloud_demo.config import settings

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 50 * 1024 * 1024
MAX_ZIP_ENTRIES = 250


class InvalidDocumentError(ValueError):
    """Erro de validação de um documento enviado."""


def _safe_filename(filename: str) -> str:
    if not filename or "\x00" in filename:
        raise InvalidDocumentError("Nome de arquivo inválido.")

    basename = filename.replace("\\", "/").rsplit("/", 1)[-1].strip()

    safe_name = re.sub(r"[^\w.-]", "_", basename, flags=re.UNICODE)
    safe_name = safe_name.strip(" .")

    if not safe_name or safe_name in {".", ".."}:
        raise InvalidDocumentError("Nome de arquivo inválido.")

    if Path(safe_name).suffix.lower() != ".xlsx":
        raise InvalidDocumentError("Somente arquivos .xlsx são permitidos.")

    stem = Path(safe_name).stem[:100]
    return f"{stem}.xlsx"


def _validate_xlsx(content: bytes) -> None:
    if not content:
        raise InvalidDocumentError("O arquivo está vazio.")

    if len(content) > MAX_UPLOAD_BYTES:
        raise InvalidDocumentError("O arquivo ultrapassa o limite de 10 MB.")

    if not content.startswith(b"PK"):
        raise InvalidDocumentError("O arquivo não possui uma estrutura XLSX válida.")

    try:
        with ZipFile(BytesIO(content)) as archive:
            entries = archive.infolist()

            if len(entries) > MAX_ZIP_ENTRIES:
                raise InvalidDocumentError("O arquivo possui conteúdo excessivo.")

            total_size = sum(entry.file_size for entry in entries)

            if total_size > MAX_UNCOMPRESSED_BYTES:
                raise InvalidDocumentError("O conteúdo descompactado é muito grande.")

            required_files = {
                "[Content_Types].xml",
                "xl/workbook.xml",
            }

            if not required_files.issubset(archive.namelist()):
                raise InvalidDocumentError("Estrutura de planilha inválida.")

            if archive.testzip() is not None:
                raise InvalidDocumentError("O arquivo possui conteúdo corrompido.")

        workbook = load_workbook(
            BytesIO(content),
            read_only=True,
            data_only=True,
        )

        try:
            if not workbook.sheetnames:
                raise InvalidDocumentError("A planilha não possui abas.")
        finally:
            workbook.close()

    except InvalidDocumentError:
        raise
    except Exception:
        raise InvalidDocumentError("Não foi possível validar a planilha Excel.") from None


def init_database() -> None:
    upload_directory = settings.storage_path / "uploads"

    upload_directory.mkdir(parents=True, exist_ok=True)
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(settings.database_path)) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS uploads (
                id TEXT PRIMARY KEY,
                original_filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL UNIQUE,
                sha256 TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                version INTEGER NOT NULL,
                uploaded_at TEXT NOT NULL
            )
            """
        )

        connection.commit()


def save_document(filename: str, content: bytes) -> dict:
    safe_name = _safe_filename(filename)
    _validate_xlsx(content)
    init_database()

    upload_directory = (settings.storage_path / "uploads").resolve()
    stored_path: Path | None = None
    file_created = False

    document_id = uuid4().hex
    checksum = hashlib.sha256(content).hexdigest()
    uploaded_at = datetime.now(timezone.utc).isoformat()

    connection = sqlite3.connect(settings.database_path, timeout=10)
    connection.row_factory = sqlite3.Row

    try:
        connection.execute("BEGIN IMMEDIATE")

        row = connection.execute(
            """
            SELECT COALESCE(MAX(version), 0) AS current_version
            FROM uploads
            WHERE original_filename = ?
            """,
            (safe_name,),
        ).fetchone()

        version = row["current_version"] + 1

        stored_filename = f"{document_id}_v{version}_{safe_name}"

        stored_path = (upload_directory / stored_filename).resolve()

        if stored_path.parent != upload_directory:
            raise InvalidDocumentError("Destino de armazenamento inválido.")

        # Criação exclusiva: não sobrescreve um arquivo existente.
        with stored_path.open("xb") as file:
            file_created = True
            file.write(content)

        connection.execute(
            """
            INSERT INTO uploads (
                id,
                original_filename,
                stored_filename,
                sha256,
                size_bytes,
                version,
                uploaded_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                document_id,
                safe_name,
                stored_filename,
                checksum,
                len(content),
                version,
                uploaded_at,
            ),
        )

        connection.commit()

    except Exception:
        connection.rollback()

        if file_created and stored_path is not None:
            stored_path.unlink(missing_ok=True)

        raise

    finally:
        connection.close()

    return {
        "id": document_id,
        "filename": safe_name,
        "stored_filename": stored_filename,
        "sha256": checksum,
        "size_bytes": len(content),
        "version": version,
        "uploaded_at": uploaded_at,
    }


def list_documents() -> list[dict]:
    init_database()

    with closing(sqlite3.connect(settings.database_path)) as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT
                id,
                original_filename,
                stored_filename,
                sha256,
                size_bytes,
                version,
                uploaded_at
            FROM uploads
            ORDER BY uploaded_at DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]
