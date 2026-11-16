from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from crm_cloud_demo.config import settings

from .routes import router

app = FastAPI(
    title="CRM Demonstrativo",
    description="Aplicação fictícia para demonstração de automação web.",
    debug=settings.app_debug,
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.crm_session_secret,
    session_cookie="crm_demo_session",
    max_age=3600,
    same_site="lax",
    https_only=False,
)

app.include_router(router)
