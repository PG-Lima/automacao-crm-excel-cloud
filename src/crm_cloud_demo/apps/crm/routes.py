from __future__ import annotations

import asyncio
import secrets
from datetime import date, timedelta
from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from crm_cloud_demo.config import settings
from crm_cloud_demo.currency import ExchangeRateError, convert_brl_to_usd, get_brl_to_usd_rate
from crm_cloud_demo.localization import (
    get_language,
    get_translations,
    safe_next_path,
    template_context,
    translate_error,
)

from .services import create_excel_report, get_deals

router = APIRouter()

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def _is_authenticated(request: Request) -> bool:
    return bool(request.session.get("username"))


def _parse_date_range(
    start_date: str | None,
    end_date: str | None,
) -> tuple[date, date]:
    today = date.today()

    try:
        start = (
            date.fromisoformat(start_date)
            if start_date
            else today - timedelta(days=settings.report_default_days)
        )

        end = date.fromisoformat(end_date) if end_date else today

    except ValueError as exc:
        raise ValueError("Informe datas válidas no formato AAAA-MM-DD.") from exc

    if start > end:
        raise ValueError("A data inicial não pode ser posterior à data final.")

    return start, end


@router.get("/language/{language}")
async def switch_language(request: Request, language: str, next_path: str = "/"):
    request.session["language"] = language if language in {"pt", "en"} else "pt"
    return RedirectResponse(safe_next_path(next_path), status_code=303)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if _is_authenticated(request):
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context=template_context(request, error=None),
    )


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    valid_username = secrets.compare_digest(
        username.strip(),
        settings.crm_demo_username,
    )

    valid_password = secrets.compare_digest(
        password,
        settings.crm_demo_password,
    )

    if not (valid_username and valid_password):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context=template_context(
                request,
                error=template_context(request)["t"]["invalid_credentials"],
            ),
            status_code=401,
        )

    language = get_language(request)
    request.session.clear()
    request.session["language"] = language
    request.session["username"] = settings.crm_demo_username

    return RedirectResponse("/", status_code=303)


@router.post("/logout")
async def logout(request: Request):
    language = get_language(request)
    request.session.clear()
    request.session["language"] = language
    return RedirectResponse("/login", status_code=303)


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not _is_authenticated(request):
        return RedirectResponse("/login", status_code=303)

    start_date, end_date = _parse_date_range(None, None)
    deals = get_deals(start_date, end_date)
    language = get_language(request)
    total_value_brl = sum(deal["valor"] for deal in deals)
    total_display_value = total_value_brl
    exchange_rate_note = None
    exchange_rate_error = False

    if language == "en":
        try:
            exchange_rate = await asyncio.to_thread(get_brl_to_usd_rate)
            total_display_value = convert_brl_to_usd(
                total_value_brl,
                exchange_rate.rate,
            )
            for deal in deals:
                deal["display_value"] = convert_brl_to_usd(
                    deal["valor"],
                    exchange_rate.rate,
                )

            exchange_rate_note = get_translations(language)["exchange_rate_note"].format(
                rate=f"{exchange_rate.rate:.6f}",
                date=exchange_rate.rate_date.isoformat(),
            )
        except ExchangeRateError:
            total_display_value = None
            exchange_rate_error = True
            for deal in deals:
                deal["display_value"] = None
    else:
        for deal in deals:
            deal["display_value"] = deal["valor"]

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=template_context(
            request,
            username=request.session["username"],
            deals=deals,
            total_deals=len(deals),
            total_value=total_display_value,
            exchange_rate_note=exchange_rate_note,
            exchange_rate_error=exchange_rate_error,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            error=None,
        ),
    )


@router.get("/reports/download")
async def download_report(
    request: Request,
    start_date: str | None = None,
    end_date: str | None = None,
):
    if not _is_authenticated(request):
        return RedirectResponse("/login", status_code=303)

    try:
        start, end = _parse_date_range(start_date, end_date)
    except ValueError as exc:
        return HTMLResponse(translate_error(str(exc), get_language(request)), status_code=400)

    deals = get_deals(start, end)
    language = get_language(request)

    if language == "en":
        try:
            exchange_rate = await asyncio.to_thread(get_brl_to_usd_rate)
        except ExchangeRateError:
            message = get_translations(language)["exchange_rate_unavailable"]
            return HTMLResponse(message, status_code=503)

        report = create_excel_report(
            deals,
            start,
            end,
            language="en",
            exchange_rate=exchange_rate.rate,
            rate_date=exchange_rate.rate_date,
        )
        filename = f"crm-report-{start:%Y%m%d}-{end:%Y%m%d}.xlsx"
    else:
        report = create_excel_report(deals, start, end)
        filename = f"crm-relatorio-{start:%Y%m%d}-{end:%Y%m%d}.xlsx"

    return Response(
        content=report.getvalue(),
        media_type=("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
