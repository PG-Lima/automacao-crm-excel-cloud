from __future__ import annotations

from pathlib import Path

import pytest

from crm_cloud_demo import config


@pytest.mark.parametrize("value", ["1", "true", "YES", "On"])
def test_get_bool_accepts_true_values(monkeypatch, value):
    monkeypatch.setenv("TEST_BOOLEAN", value)
    assert config._get_bool("TEST_BOOLEAN", False) is True


@pytest.mark.parametrize("value", ["0", "false", "NO", "Off"])
def test_get_bool_accepts_false_values(monkeypatch, value):
    monkeypatch.setenv("TEST_BOOLEAN", value)
    assert config._get_bool("TEST_BOOLEAN", True) is False


def test_get_bool_uses_default_when_environment_variable_is_missing(monkeypatch):
    monkeypatch.delenv("TEST_BOOLEAN", raising=False)
    assert config._get_bool("TEST_BOOLEAN", True) is True


def test_get_bool_rejects_unrecognized_values(monkeypatch):
    monkeypatch.setenv("TEST_BOOLEAN", "sometimes")
    with pytest.raises(ValueError, match="Valor booleano inválido"):
        config._get_bool("TEST_BOOLEAN", False)


def test_get_positive_int_accepts_positive_value(monkeypatch):
    monkeypatch.setenv("TEST_TIMEOUT", "15000")
    assert config._get_positive_int("TEST_TIMEOUT", 1000) == 15000


@pytest.mark.parametrize("value", ["0", "-1"])
def test_get_positive_int_rejects_non_positive_values(monkeypatch, value):
    monkeypatch.setenv("TEST_TIMEOUT", value)
    with pytest.raises(ValueError, match="maior que zero"):
        config._get_positive_int("TEST_TIMEOUT", 1000)


def test_get_path_resolves_relative_path_from_project_root(monkeypatch):
    monkeypatch.setenv("TEST_PATH", "tmp/test-data")
    assert config._get_path("TEST_PATH", ".").as_posix().endswith(
        "tmp/test-data"
    )
    assert config._get_path("TEST_PATH", ".").is_absolute()


def test_load_settings_requires_all_demo_credentials(monkeypatch):
    for key in (
        "CRM_DEMO_USERNAME",
        "CRM_DEMO_PASSWORD",
        "CLOUD_DEMO_USERNAME",
        "CLOUD_DEMO_PASSWORD",
    ):
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(ValueError, match="credenciais demonstrativas do CRM"):
        config.load_settings()


def test_load_settings_rejects_short_session_secrets(monkeypatch):
    monkeypatch.setenv("CRM_DEMO_USERNAME", "demo")
    monkeypatch.setenv("CRM_DEMO_PASSWORD", "demo-password")
    monkeypatch.setenv("CLOUD_DEMO_USERNAME", "cloud-demo")
    monkeypatch.setenv("CLOUD_DEMO_PASSWORD", "cloud-password")
    monkeypatch.setenv("CRM_SESSION_SECRET", "short")
    monkeypatch.setenv(
        "CLOUD_SESSION_SECRET",
        "cloud-test-secret-that-is-at-least-32-characters",
    )

    with pytest.raises(ValueError, match="pelo menos 32 caracteres"):
        config.load_settings()


def test_load_settings_builds_paths_and_reads_values(monkeypatch, tmp_path):
    monkeypatch.setenv("CRM_DEMO_USERNAME", "crm-user")
    monkeypatch.setenv("CRM_DEMO_PASSWORD", "crm-password")
    monkeypatch.setenv("CLOUD_DEMO_USERNAME", "cloud-user")
    monkeypatch.setenv("CLOUD_DEMO_PASSWORD", "cloud-password")
    monkeypatch.setenv("CRM_SESSION_SECRET", "crm-secret-value-longer-than-32-characters")
    monkeypatch.setenv(
        "CLOUD_SESSION_SECRET",
        "cloud-secret-value-longer-than-32-characters",
    )
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path / "storage"))
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "storage" / "db.sqlite"))
    monkeypatch.setenv("REPORT_DEFAULT_DAYS", "45")
    monkeypatch.setenv("PLAYWRIGHT_HEADLESS", "false")

    settings = config.load_settings()

    assert settings.crm_demo_username == "crm-user"
    assert settings.cloud_demo_username == "cloud-user"
    assert settings.storage_path == tmp_path / "storage"
    assert settings.database_path == tmp_path / "storage" / "db.sqlite"
    assert settings.report_default_days == 45
    assert settings.playwright_headless is False
