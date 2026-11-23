from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO

from crm_cloud_demo.currency import convert_brl_to_usd

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


def _build_demo_records() -> list[dict]:
    today = date.today()

    return [
        {
            "id": "CRM-1001",
            "empresa": "Aurora Comércio",
            "responsavel": "Camila",
            "etapa": "Novo contato",
            "valor": 12500.00,
            "data": today - timedelta(days=2),
        },
        {
            "id": "CRM-1002",
            "empresa": "Horizonte Tech",
            "responsavel": "Rafael",
            "etapa": "Em negociação",
            "valor": 8700.00,
            "data": today - timedelta(days=5),
        },
        {
            "id": "CRM-1003",
            "empresa": "Nuvem Digital",
            "responsavel": "Alex",
            "etapa": "Proposta enviada",
            "valor": 15300.00,
            "data": today - timedelta(days=8),
        },
        {
            "id": "CRM-1004",
            "empresa": "Ponto Criativo",
            "responsavel": "Camila",
            "etapa": "Ganho",
            "valor": 6200.00,
            "data": today - timedelta(days=12),
        },
        {
            "id": "CRM-1005",
            "empresa": "Orion Sistemas",
            "responsavel": "Rafael",
            "etapa": "Perdido",
            "valor": 9800.00,
            "data": today - timedelta(days=18),
        },
        {
            "id": "CRM-1006",
            "empresa": "Vértice Soluções",
            "responsavel": "Alex",
            "etapa": "Em negociação",
            "valor": 21400.00,
            "data": today - timedelta(days=23),
        },
        {
            "id": "CRM-1007",
            "empresa": "Atlas Serviços",
            "responsavel": "Camila",
            "etapa": "Ganho",
            "valor": 7400.00,
            "data": today - timedelta(days=31),
        },
        {
            "id": "CRM-1008",
            "empresa": "Pixel Studio",
            "responsavel": "Rafael",
            "etapa": "Novo contato",
            "valor": 5600.00,
            "data": today - timedelta(days=42),
        },
        {
            "id": "CRM-1009",
            "empresa": "Delta Consultoria",
            "responsavel": "Alex",
            "etapa": "Proposta enviada",
            "valor": 18900.00,
            "data": today - timedelta(days=55),
        },
        {
            "id": "CRM-1010",
            "empresa": "Prisma Tecnologia",
            "responsavel": "Camila",
            "etapa": "Em negociação",
            "valor": 11200.00,
            "data": today - timedelta(days=68),
        },
    ]


def get_deals(
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[dict]:
    records = _build_demo_records()

    if start_date is not None:
        records = [record for record in records if record["data"] >= start_date]

    if end_date is not None:
        records = [record for record in records if record["data"] <= end_date]

    return records


def create_excel_report(
    records: list[dict],
    start_date: date,
    end_date: date,
    language: str = "pt",
    exchange_rate: Decimal | None = None,
    rate_date: date | None = None,
) -> BytesIO:
    is_english = language == "en"

    if is_english and (
        exchange_rate is None or rate_date is None or exchange_rate <= 0
    ):
        raise ValueError("A valid BRL/USD exchange rate and date are required for English reports.")

    workbook = Workbook()

    sheet = workbook.active
    sheet.title = "Deals" if is_english else "Negociações"

    headers = (
        [
            "ID",
            "Company",
            "Owner",
            "Stage",
            "Amount (USD)",
            "Entry date",
        ]
        if is_english
        else [
            "Identificador",
            "Empresa",
            "Responsável",
            "Etapa",
            "Valor (R$)",
            "Data de entrada",
        ]
    )

    sheet.append(headers)

    header_fill = PatternFill(
        fill_type="solid",
        fgColor="243B53",
    )

    for cell in sheet[1]:
        cell.font = Font(color="FFFFFF", bold=True)
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    stage_labels = {
        "Ganho": "Won",
        "Em negociação": "In negotiation",
        "Proposta enviada": "Proposal sent",
        "Perdido": "Lost",
        "Novo contato": "New lead",
    }

    for record in records:
        stage = (
            stage_labels.get(record["etapa"], record["etapa"])
            if is_english
            else record["etapa"]
        )
        sheet.append(
            [
                record["id"],
                record["empresa"],
                record["responsavel"],
                stage,
                (
                    float(convert_brl_to_usd(record["valor"], exchange_rate))
                    if is_english and exchange_rate is not None
                    else record["valor"]
                ),
                record["data"],
            ]
        )

    for row in range(2, sheet.max_row + 1):
        sheet.cell(row=row, column=5).number_format = (
            '"USD" #,##0.00' if is_english else "R$ #,##0.00"
        )
        sheet.cell(row=row, column=6).number_format = (
            "MM/DD/YYYY" if is_english else "DD/MM/YYYY"
        )

    column_widths = [18, 25, 18, 22, 18, 20]

    for index, width in enumerate(column_widths, start=1):
        sheet.column_dimensions[get_column_letter(index)].width = width

    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions

    summary = workbook.create_sheet("Summary" if is_english else "Resumo")

    if is_english:
        summary.append(["CRM REPORT - DEMONSTRATION"])
        summary.append(["Start date", start_date])
        summary.append(["End date", end_date])
        summary.append(["Total deals", len(records)])
        summary.append(
            [
                "Total value (USD)",
                float(
                    convert_brl_to_usd(
                        sum(record["valor"] for record in records),
                        exchange_rate,
                    )
                ),
            ]
        )
        summary.append(["Exchange rate (1 BRL to USD)", float(exchange_rate)])
        summary.append(["Rate date", rate_date])
        summary.append(["Rate source", "Frankfurter"])
    else:
        summary.append(["RELATÓRIO CRM - DEMONSTRAÇÃO"])
        summary.append(["Período inicial", start_date])
        summary.append(["Período final", end_date])
        summary.append(["Total de negociações", len(records)])
        summary.append(
            [
                "Valor total",
                sum(record["valor"] for record in records),
            ]
        )

    summary["A1"].font = Font(bold=True, size=14, color="243B53")
    summary["B5"].number_format = '"USD" #,##0.00' if is_english else "R$ #,##0.00"
    if is_english:
        summary["B6"].number_format = '0.000000 "USD per BRL"'
        summary["B7"].number_format = "MM/DD/YYYY"
    summary["B2"].number_format = "MM/DD/YYYY" if is_english else "DD/MM/YYYY"
    summary["B3"].number_format = "MM/DD/YYYY" if is_english else "DD/MM/YYYY"
    summary.column_dimensions["A"].width = 30
    summary.column_dimensions["B"].width = 22

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return output
