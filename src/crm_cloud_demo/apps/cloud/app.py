from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from crm_cloud_demo.config import settings

from .routes import router
from .storage import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield


app = FastAPI(
    title="Biblioteca em Nuvem Demonstrativa",
    description="Sistema fictício para demonstração de automação.",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.cloud_session_secret,
    session_cookie="cloud_demo_session",
    max_age=3600,
    same_site="lax",
    https_only=False,
)

app.include_router(router)
