from types import SimpleNamespace

import pytest

from crm_cloud_demo.localization import (
    get_language,
    get_translations,
    safe_next_path,
    template_context,
    translate_error,
)


def make_request(session: dict | None = None):
    return SimpleNamespace(session=session or {})


def test_language_defaults_to_portuguese():
    assert get_language(make_request()) == "pt"


def test_english_language_is_read_from_session():
    assert get_language(make_request({"language": "en"})) == "en"


def test_unsupported_language_falls_back_to_portuguese():
    assert get_language(make_request({"language": "es"})) == "pt"


def test_template_context_contains_language_and_translations():
    context = template_context(make_request({"language": "en"}), username="demo")

    assert context["lang"] == "en"
    assert context["t"]["html_lang"] == "en"
    assert context["t"]["username"] == "Username"
    assert context["username"] == "demo"


def test_portuguese_and_english_translations_are_available():
    assert get_translations("pt")["document_library"] == "Biblioteca de documentos"
    assert get_translations("en")["document_library"] == "Document library"


def test_known_validation_error_is_translated():
    message = "Somente arquivos .xlsx são permitidos."

    assert translate_error(message, "en") == "Only .xlsx files are allowed."
    assert translate_error(message, "pt") == message


def test_unknown_error_is_preserved():
    message = "An unexpected storage error occurred."

    assert translate_error(message, "en") == message


@pytest.mark.parametrize(
    "next_path",
    [
        "/",
        "/login",
        "/?success=Upload%20completed",
        "/reports/download?start_date=2026-01-01",
    ],
)
def test_safe_next_path_accepts_local_paths(next_path: str):
    assert safe_next_path(next_path) == next_path


@pytest.mark.parametrize(
    "next_path",
    [
        None,
        "",
        "https://example.com",
        "//example.com",
        "/\\\\example.com",
        "login",
    ],
)
def test_safe_next_path_rejects_external_or_invalid_paths(next_path: str | None):
    assert safe_next_path(next_path, fallback="/login") == "/login"
