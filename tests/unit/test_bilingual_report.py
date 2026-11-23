from datetime import date
from decimal import Decimal
from io import BytesIO

from openpyxl import load_workbook

from crm_cloud_demo.apps.crm.services import create_excel_report


def sample_records() -> list[dict]:
    return [
        {
            "id": "CRM-1001",
            "empresa": "Aurora Comércio",
            "responsavel": "Camila",
            "etapa": "Em negociação",
            "valor": 8700.50,
            "data": date(2026, 11, 20),
        }
    ]


def open_report(report: BytesIO):
    return load_workbook(report, data_only=True)


def test_excel_report_uses_portuguese_by_default():
    workbook = open_report(
        create_excel_report(
            sample_records(),
            date(2026, 11, 1),
            date(2026, 11, 23),
        )
    )

    assert workbook.sheetnames == ["Negociações", "Resumo"]
    assert workbook["Negociações"]["A1"].value == "Identificador"
    assert workbook["Negociações"]["D2"].value == "Em negociação"
    assert workbook["Resumo"]["A2"].value == "Período inicial"


def test_excel_report_can_be_generated_in_english():
    workbook = open_report(
        create_excel_report(
            sample_records(),
            date(2026, 11, 1),
            date(2026, 11, 23),
            language="en",
            exchange_rate=Decimal("0.20"),
            rate_date=date(2026, 11, 21),
        )
    )

    assert workbook.sheetnames == ["Deals", "Summary"]
    assert workbook["Deals"]["A1"].value == "ID"
    assert workbook["Deals"]["D2"].value == "In negotiation"
    assert workbook["Deals"]["E1"].value == "Amount (USD)"
    assert workbook["Deals"]["E2"].value == 1740.10
    assert workbook["Deals"]["E2"].number_format == '"USD" #,##0.00'
    assert workbook["Summary"]["A2"].value == "Start date"
    assert workbook["Summary"]["A5"].value == "Total value (USD)"
    assert workbook["Summary"]["B5"].value == 1740.10
    assert workbook["Summary"]["A6"].value == "Exchange rate (1 BRL to USD)"
    assert workbook["Summary"]["B6"].value == 0.20
    assert workbook["Summary"]["A7"].value == "Rate date"
    assert workbook["Summary"]["B7"].value.date() == date(2026, 11, 21)


def test_english_excel_report_requires_a_reference_rate():
    import pytest

    with pytest.raises(ValueError, match="exchange rate and date are required"):
        create_excel_report(
            sample_records(),
            date(2026, 11, 1),
            date(2026, 11, 23),
            language="en",
        )
