from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env", override=False)


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    normalized = value.strip().lower()

    if normalized in {"1", "true", "yes", "on"}:
        return True

    if normalized in {"0", "false", "no", "off"}:
        return False

    raise ValueError(f"Valor booleano inválido para {name}")


def _get_positive_int(name: str, default: int) -> int:
    value = int(os.getenv(name, str(default)))

    if value <= 0:
        raise ValueError(f"{name} precisa ser maior que zero.")

    return value


def _get_path(name: str, default: str) -> Path:
    path = Path(os.getenv(name, default))

    if not path.is_absolute():
        path = PROJECT_ROOT / path

    return path.resolve()


@dataclass(frozen=True, slots=True)
class Settings:
    app_env: str
    app_debug: bool
    crm_base_url: str
    cloud_base_url: str

    crm_demo_username: str
    crm_demo_password: str
    crm_session_secret: str

    cloud_demo_username: str
    cloud_demo_password: str
    cloud_session_secret: str

    playwright_headless: bool
    automation_timeout: int
    playwright_browsers_path: Path

    storage_path: Path
    database_path: Path
    report_default_days: int


def load_settings() -> Settings:
    crm_username = os.getenv("CRM_DEMO_USERNAME", "")
    crm_password = os.getenv("CRM_DEMO_PASSWORD", "")

    cloud_username = os.getenv("CLOUD_DEMO_USERNAME", "")
    cloud_password = os.getenv("CLOUD_DEMO_PASSWORD", "")

    if not crm_username or not crm_password:
        raise ValueError("Configure as credenciais demonstrativas do CRM.")

    if not cloud_username or not cloud_password:
        raise ValueError("Configure as credenciais demonstrativas da biblioteca.")

    crm_secret = os.getenv("CRM_SESSION_SECRET") or secrets.token_urlsafe(32)
    cloud_secret = os.getenv("CLOUD_SESSION_SECRET") or secrets.token_urlsafe(32)

    if len(crm_secret) < 32 or len(cloud_secret) < 32:
        raise ValueError("As chaves de sessão precisam ter pelo menos 32 caracteres.")

    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        app_debug=_get_bool("APP_DEBUG", False),
        crm_base_url=os.getenv("CRM_BASE_URL", "http://127.0.0.1:8000"),
        cloud_base_url=os.getenv("CLOUD_BASE_URL", "http://127.0.0.1:8001"),
        crm_demo_username=crm_username,
        crm_demo_password=crm_password,
        crm_session_secret=crm_secret,
        cloud_demo_username=cloud_username,
        cloud_demo_password=cloud_password,
        cloud_session_secret=cloud_secret,
        playwright_headless=_get_bool("PLAYWRIGHT_HEADLESS", True),
        automation_timeout=_get_positive_int("AUTOMATION_TIMEOUT", 30000),
        playwright_browsers_path=_get_path("PLAYWRIGHT_BROWSERS_PATH", "./.playwright-browsers"),
        storage_path=_get_path("STORAGE_PATH", "./storage"),
        database_path=_get_path("DATABASE_PATH", "./storage/metadata.db"),
        report_default_days=_get_positive_int("REPORT_DEFAULT_DAYS", 30),
    )


settings = load_settings()

os.environ.setdefault(
    "PLAYWRIGHT_BROWSERS_PATH",
    str(settings.playwright_browsers_path),
)
