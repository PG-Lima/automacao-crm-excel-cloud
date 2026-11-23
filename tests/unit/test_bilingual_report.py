from datetime import date
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
        )
    )

    assert workbook.sheetnames == ["Deals", "Summary"]
    assert workbook["Deals"]["A1"].value == "ID"
    assert workbook["Deals"]["D2"].value == "In negotiation"
    assert workbook["Summary"]["A2"].value == "Start date"
    assert workbook["Deals"]["E2"].number_format == '"BRL" #,##0.00'
