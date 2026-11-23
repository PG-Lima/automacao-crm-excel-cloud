from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook, load_workbook

from crm_cloud_demo.apps.cloud import storage as cloud_storage
from crm_cloud_demo.apps.crm import routes as crm_routes
from crm_cloud_demo.config import settings
from crm_cloud_demo.currency import ExchangeRate, ExchangeRateError


@pytest.fixture
def crm_client():
    from crm_cloud_demo.apps.crm.app import app

    with TestClient(app) as client:
        yield client


@pytest.fixture
def cloud_client(tmp_path, monkeypatch):
    isolated_settings = replace(
        settings,
        storage_path=tmp_path / "storage",
        database_path=tmp_path / "storage" / "metadata.db",
    )
    monkeypatch.setattr(cloud_storage, "settings", isolated_settings)

    from crm_cloud_demo.apps.cloud.app import app

    with TestClient(app) as client:
        yield client, isolated_settings


def login(client: TestClient, username: str, password: str) -> None:
    response = client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def make_xlsx_bytes() -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Deals"
    sheet.append(["ID", "Company", "Amount"])
    sheet.append(["CRM-1001", "Example Ltd", 12500])
    output = BytesIO()
    workbook.save(output)
    return output.getvalue()


def fixed_exchange_rate() -> ExchangeRate:
    return ExchangeRate(
        base="BRL",
        quote="USD",
        rate=Decimal("0.20"),
        rate_date=date(2026, 11, 20),
    )


def test_crm_requires_login_and_rejects_invalid_credentials(crm_client):
    response = crm_client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    response = crm_client.post(
        "/login",
        data={"username": "wrong", "password": "wrong"},
    )
    assert response.status_code == 401
    assert "Invalid username or password" not in response.text
    assert "inválidos" in response.text


def test_crm_portuguese_dashboard_keeps_brl_and_does_not_fetch_rate(
    crm_client,
    monkeypatch,
):
    def unexpected_rate_lookup():
        raise AssertionError("Portuguese dashboard must not request an exchange rate")

    monkeypatch.setattr(crm_routes, "get_brl_to_usd_rate", unexpected_rate_lookup)
    login(crm_client, settings.crm_demo_username, settings.crm_demo_password)

    response = crm_client.get("/")
    assert response.status_code == 200
    assert "Visão geral" in response.text
    assert "R$" in response.text
    assert "US$" not in response.text


def test_crm_english_dashboard_converts_amounts_and_shows_rate(
    crm_client,
    monkeypatch,
):
    monkeypatch.setattr(crm_routes, "get_brl_to_usd_rate", fixed_exchange_rate)

    response = crm_client.get("/language/en?next_path=/login", follow_redirects=False)
    assert response.status_code == 303

    login(crm_client, settings.crm_demo_username, settings.crm_demo_password)
    response = crm_client.get("/")

    assert response.status_code == 200
    assert "Overview" in response.text
    assert "Amount (USD)" in response.text
    assert "US$" in response.text
    assert "0.200000 USD per BRL" in response.text
    assert "11/20/2026" in response.text


def test_crm_english_dashboard_reports_rate_unavailability(
    crm_client,
    monkeypatch,
):
    def unavailable_rate():
        raise ExchangeRateError("provider unavailable")

    monkeypatch.setattr(crm_routes, "get_brl_to_usd_rate", unavailable_rate)
    crm_client.get("/language/en?next_path=/login", follow_redirects=False)
    login(crm_client, settings.crm_demo_username, settings.crm_demo_password)

    response = crm_client.get("/")
    assert response.status_code == 200
    assert "USD conversion is temporarily unavailable" in response.text
    assert "—" in response.text


def test_crm_english_excel_export_contains_converted_values_and_rate_metadata(
    crm_client,
    monkeypatch,
):
    monkeypatch.setattr(crm_routes, "get_brl_to_usd_rate", fixed_exchange_rate)
    crm_client.get("/language/en?next_path=/login", follow_redirects=False)
    login(crm_client, settings.crm_demo_username, settings.crm_demo_password)

    start = (date.today() - timedelta(days=90)).isoformat()
    end = date.today().isoformat()
    response = crm_client.get(
        f"/reports/download?start_date={start}&end_date={end}",
    )

    assert response.status_code == 200
    assert "crm-report-" in response.headers["content-disposition"]

    workbook = load_workbook(BytesIO(response.content), data_only=True)
    assert workbook.sheetnames == ["Deals", "Summary"]
    assert workbook["Deals"]["E1"].value == "Amount (USD)"
    assert workbook["Summary"]["A6"].value == "Exchange rate (1 BRL to USD)"
    assert workbook["Summary"]["B6"].value == 0.2


def test_crm_excel_export_in_portuguese_does_not_need_exchange_rate(
    crm_client,
    monkeypatch,
):
    def unexpected_rate_lookup():
        raise AssertionError("Portuguese report must not request an exchange rate")

    monkeypatch.setattr(crm_routes, "get_brl_to_usd_rate", unexpected_rate_lookup)
    login(crm_client, settings.crm_demo_username, settings.crm_demo_password)

    response = crm_client.get("/reports/download")
    assert response.status_code == 200
    assert "crm-relatorio-" in response.headers["content-disposition"]

    workbook = load_workbook(BytesIO(response.content), data_only=True)
    assert workbook.sheetnames == ["Negociações", "Resumo"]
    assert workbook["Negociações"]["E1"].value == "Valor (R$)"


def test_crm_english_export_returns_service_unavailable_when_rate_is_missing(
    crm_client,
    monkeypatch,
):
    def unavailable_rate():
        raise ExchangeRateError("provider unavailable")

    monkeypatch.setattr(crm_routes, "get_brl_to_usd_rate", unavailable_rate)
    crm_client.get("/language/en?next_path=/login", follow_redirects=False)
    login(crm_client, settings.crm_demo_username, settings.crm_demo_password)

    response = crm_client.get("/reports/download")
    assert response.status_code == 503
    assert "USD conversion is temporarily unavailable" in response.text


@pytest.mark.parametrize(
    ("query", "expected_status"),
    [
        ("start_date=not-a-date", 400),
        ("start_date=2026-12-02&end_date=2026-12-01", 400),
    ],
)
def test_crm_export_rejects_invalid_date_ranges(crm_client, query, expected_status):
    login(crm_client, settings.crm_demo_username, settings.crm_demo_password)
    response = crm_client.get(f"/reports/download?{query}")
    assert response.status_code == expected_status


def test_cloud_requires_login_and_supports_english_language(cloud_client):
    client, _ = cloud_client
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    client.get("/language/en?next_path=/login", follow_redirects=False)
    login(client, settings.cloud_demo_username, settings.cloud_demo_password)

    response = client.get("/")
    assert response.status_code == 200
    assert "Document library" in response.text
    assert "Upload document" in response.text


def test_cloud_rejects_invalid_credentials(cloud_client):
    client, _ = cloud_client
    response = client.post(
        "/login",
        data={"username": "wrong", "password": "wrong"},
    )
    assert response.status_code == 401
    assert "Usuário ou senha inválidos" in response.text


def test_cloud_upload_persists_file_hash_and_version_history(cloud_client):
    client, isolated_settings = cloud_client
    login(client, settings.cloud_demo_username, settings.cloud_demo_password)
    content = make_xlsx_bytes()

    response = client.post(
        "/upload",
        files={
            "file": (
                "sales-report.xlsx",
                content,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "Upload" in response.headers["location"]

    dashboard = client.get(response.headers["location"])
    assert dashboard.status_code == 200
    assert "sales-report.xlsx" in dashboard.text
    assert "v1" in dashboard.text

    stored = cloud_storage.list_documents()
    assert len(stored) == 1
    assert stored[0]["version"] == 1
    assert (isolated_settings.storage_path / "uploads" / stored[0]["stored_filename"]).is_file()

    second = client.post(
        "/upload",
        files={"file": ("sales-report.xlsx", content, "application/octet-stream")},
        follow_redirects=False,
    )
    assert second.status_code == 303
    success_message = parse_qs(urlsplit(second.headers["location"]).query)["success"][0]
    assert success_message == "Upload concluído. Versão 2"

    stored = cloud_storage.list_documents()
    assert len(stored) == 2
    assert {item["version"] for item in stored} == {1, 2}


def test_cloud_upload_rejects_non_xlsx_files(cloud_client):
    client, _ = cloud_client
    login(client, settings.cloud_demo_username, settings.cloud_demo_password)

    response = client.post(
        "/upload",
        files={"file": ("report.csv", b"id,value\n1,100", "text/csv")},
        follow_redirects=False,
    )
    assert response.status_code == 303

    dashboard = client.get(response.headers["location"])
    assert dashboard.status_code == 200
    assert "Somente arquivos .xlsx são permitidos" in dashboard.text
    assert cloud_storage.list_documents() == []


def test_cloud_upload_rejects_corrupted_xlsx_files(cloud_client):
    client, _ = cloud_client
    login(client, settings.cloud_demo_username, settings.cloud_demo_password)

    response = client.post(
        "/upload",
        files={"file": ("corrupted.xlsx", b"PK\x03\x04not-a-workbook", "application/octet-stream")},
        follow_redirects=False,
    )
    assert response.status_code == 303

    dashboard = client.get(response.headers["location"])
    assert "Não foi possível validar a planilha Excel" in dashboard.text
    assert cloud_storage.list_documents() == []
