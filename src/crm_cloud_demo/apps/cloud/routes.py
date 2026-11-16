from __future__ import annotations

import secrets
from pathlib import Path
from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

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


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if _is_authenticated(request):
        return RedirectResponse("/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": None},
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
            context={"error": "Usuário ou senha inválidos."},
            status_code=401,
        )

    request.session.clear()
    request.session["username"] = settings.cloud_demo_username

    return RedirectResponse("/", status_code=303)


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not _is_authenticated(request):
        return RedirectResponse("/login", status_code=303)

    documents = list_documents()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "username": request.session["username"],
            "documents": documents,
            "success": request.query_params.get("success"),
            "error": request.query_params.get("error"),
        },
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
        success_message = f"Upload concluído. Versão {result['version']}"
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
