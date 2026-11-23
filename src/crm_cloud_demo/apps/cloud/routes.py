from __future__ import annotations

import secrets
from pathlib import Path
from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from crm_cloud_demo.localization import (
    get_language,
    safe_next_path,
    template_context,
    translate_error,
)

from .storage import (
    MAX_UPLOAD_BYTES,
    InvalidDocumentError,
    list_documents,
    save_document,
)

router = APIRouter()

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def _is_authenticated(request: Request) -> bool:
    return bool(request.session.get("username"))


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
    from crm_cloud_demo.config import settings

    valid_username = secrets.compare_digest(
        username.strip(),
        settings.cloud_demo_username,
    )
    valid_password = secrets.compare_digest(
        password,
        settings.cloud_demo_password,
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
    request.session["username"] = settings.cloud_demo_username

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

    documents = list_documents()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=template_context(
            request,
            username=request.session["username"],
            documents=documents,
            success=request.query_params.get("success"),
            error=(
                translate_error(request.query_params.get("error", ""), get_language(request))
                if request.query_params.get("error")
                else None
            ),
        ),
    )


@router.post("/upload")
async def upload_document(
    request: Request,
    file: Annotated[UploadFile, File()],
):

    if not _is_authenticated(request):
        return RedirectResponse("/login", status_code=303)

    try:
        content = await file.read(MAX_UPLOAD_BYTES + 1)

        result = save_document(
            filename=file.filename or "",
            content=content,
        )
        success_message = template_context(request)["t"]["upload_success"].format(
            version=result["version"]
        )
        query = urlencode({"success": success_message})

        return RedirectResponse(
            f"/?{query}",
            status_code=303,
        )

    except InvalidDocumentError as exc:
        query = urlencode({"error": str(exc)})

        return RedirectResponse(
            f"/?{query}",
            status_code=303,
        )

    finally:
        await file.close()
