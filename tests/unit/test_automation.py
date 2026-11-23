from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import anyio
import pytest

from crm_cloud_demo.automation import browser as browser_module
from crm_cloud_demo.automation import cloud as cloud_module
from crm_cloud_demo.automation import crm as crm_module
from crm_cloud_demo.automation import run as run_module
from crm_cloud_demo.config import settings


class FakePage:
    def __init__(self):
        self.default_timeout = None

    def set_default_timeout(self, timeout):
        self.default_timeout = timeout


class FakeContext:
    def __init__(self, page=None, page_error=None, close_error=None):
        self.page = page or FakePage()
        self.page_error = page_error
        self.close_error = close_error
        self.closed = False

    async def new_page(self):
        if self.page_error:
            raise self.page_error
        return self.page

    async def close(self):
        self.closed = True
        if self.close_error:
            raise self.close_error


class FakeBrowser:
    def __init__(self, context=None, context_error=None):
        self.context = context or FakeContext()
        self.context_error = context_error
        self.closed = False

    async def new_context(self, accept_downloads):
        assert accept_downloads is True
        if self.context_error:
            raise self.context_error
        return self.context

    async def close(self):
        self.closed = True


class FakePlaywrightManager:
    def __init__(self, browser):
        self.browser = browser
        self.exited = False
        self.chromium = SimpleNamespace(launch=AsyncMock(return_value=browser))

    async def __aenter__(self):
        return SimpleNamespace(chromium=self.chromium)

    async def __aexit__(self, exc_type, exc, traceback):
        self.exited = True


def install_fake_playwright(monkeypatch, browser):
    manager = FakePlaywrightManager(browser)
    monkeypatch.setattr(browser_module, "async_playwright", lambda: manager)
    return manager


def test_browser_session_closes_context_and_browser(monkeypatch):
    context = FakeContext()
    browser = FakeBrowser(context=context)
    manager = install_fake_playwright(monkeypatch, browser)

    async def scenario():
        async with browser_module.browser_session() as page:
            assert page is context.page
            assert page.default_timeout == settings.automation_timeout

    anyio.run(scenario)

    assert context.closed is True
    assert browser.closed is True
    assert manager.exited is True


def test_browser_session_closes_browser_when_context_creation_fails(monkeypatch):
    browser = FakeBrowser(context_error=RuntimeError("context failure"))
    install_fake_playwright(monkeypatch, browser)

    async def scenario():
        async with browser_module.browser_session():
            pytest.fail("The browser context should not have been entered")

    with pytest.raises(RuntimeError, match="context failure"):
        anyio.run(scenario)

    assert browser.closed is True


def test_browser_session_closes_browser_when_page_creation_fails(monkeypatch):
    context = FakeContext(page_error=RuntimeError("page failure"))
    browser = FakeBrowser(context=context)
    install_fake_playwright(monkeypatch, browser)

    async def scenario():
        async with browser_module.browser_session():
            pytest.fail("A page should not have been yielded")

    with pytest.raises(RuntimeError, match="page failure"):
        anyio.run(scenario)

    assert context.closed is True
    assert browser.closed is True


def test_browser_session_closes_browser_even_if_context_cleanup_fails(monkeypatch):
    context = FakeContext(close_error=RuntimeError("cleanup failure"))
    browser = FakeBrowser(context=context)
    install_fake_playwright(monkeypatch, browser)

    async def scenario():
        async with browser_module.browser_session():
            pass

    with pytest.raises(RuntimeError, match="cleanup failure"):
        anyio.run(scenario)

    assert context.closed is True
    assert browser.closed is True


def test_login_to_crm_fills_credentials_and_waits_for_navigation():
    username = SimpleNamespace(fill=AsyncMock())
    password = SimpleNamespace(fill=AsyncMock())
    submit = SimpleNamespace(click=AsyncMock())
    page = SimpleNamespace(
        goto=AsyncMock(),
        locator=MagicMock(side_effect=[username, password, submit]),
        wait_for_url=AsyncMock(),
    )

    anyio.run(crm_module.login_to_crm, page)

    page.goto.assert_awaited_once_with(
        f"{settings.crm_base_url}/login",
        wait_until="domcontentloaded",
    )
    username.fill.assert_awaited_once_with(settings.crm_demo_username)
    password.fill.assert_awaited_once_with(settings.crm_demo_password)
    submit.click.assert_awaited_once()
    page.wait_for_url.assert_awaited_once()


def test_login_to_cloud_fills_credentials_and_waits_for_navigation():
    username = SimpleNamespace(fill=AsyncMock())
    password = SimpleNamespace(fill=AsyncMock())
    submit = SimpleNamespace(click=AsyncMock())
    page = SimpleNamespace(
        goto=AsyncMock(),
        locator=MagicMock(side_effect=[username, password, submit]),
        wait_for_url=AsyncMock(),
    )

    anyio.run(cloud_module.login_to_cloud, page)

    page.goto.assert_awaited_once_with(
        f"{settings.cloud_base_url}/login",
        wait_until="domcontentloaded",
    )
    username.fill.assert_awaited_once_with(settings.cloud_demo_username)
    password.fill.assert_awaited_once_with(settings.cloud_demo_password)
    submit.click.assert_awaited_once()
    page.wait_for_url.assert_awaited_once()


def test_download_crm_report_saves_download_in_project_directory(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(crm_module, "PROJECT_ROOT", tmp_path)
    button = SimpleNamespace(
        count=AsyncMock(return_value=1),
        click=AsyncMock(),
    )

    class Download:
        suggested_filename = "../sales-report.xlsx"

        async def save_as(self, destination):
            Path(destination).write_bytes(b"valid demo bytes")

    download = Download()

    class DownloadContext:
        async def __aenter__(self):
            async def get_download():
                return download

            return SimpleNamespace(value=get_download())

        async def __aexit__(self, exc_type, exc, traceback):
            return False

    page = SimpleNamespace(
        locator=MagicMock(return_value=button),
        expect_download=MagicMock(return_value=DownloadContext()),
    )

    destination = anyio.run(crm_module.download_crm_report, page)

    assert destination == tmp_path / "downloads" / "sales-report.xlsx"
    assert destination.read_bytes() == b"valid demo bytes"
    button.click.assert_awaited_once()


def test_download_crm_report_fails_when_export_button_is_missing():
    button = SimpleNamespace(count=AsyncMock(return_value=0))
    page = SimpleNamespace(
        locator=MagicMock(return_value=button),
        expect_download=MagicMock(),
    )

    with pytest.raises(RuntimeError, match="não foi encontrado"):
        anyio.run(crm_module.download_crm_report, page)


def test_upload_to_cloud_uploads_file_and_returns_confirmation(tmp_path):
    report = tmp_path / "report.xlsx"
    report.write_bytes(b"demo")

    file_input = SimpleNamespace(set_input_files=AsyncMock())
    submit = SimpleNamespace(click=AsyncMock())
    success = SimpleNamespace(
        wait_for=AsyncMock(),
        inner_text=AsyncMock(return_value="Upload completed. Version 1"),
    )
    page = SimpleNamespace(
        goto=AsyncMock(),
        locator=MagicMock(side_effect=[file_input, submit, success]),
    )

    result = anyio.run(cloud_module.upload_to_cloud, page, report)

    assert result == "Upload completed. Version 1"
    page.goto.assert_awaited_once_with(
        settings.cloud_base_url,
        wait_until="domcontentloaded",
    )
    file_input.set_input_files.assert_awaited_once_with(str(report))
    submit.click.assert_awaited_once()
    success.wait_for.assert_awaited_once_with(
        state="visible",
        timeout=settings.automation_timeout,
    )


@pytest.mark.parametrize(
    ("filename", "error_type", "message"),
    [
        ("missing.xlsx", FileNotFoundError, "não encontrado"),
        ("report.csv", ValueError, "somente arquivos .xlsx"),
    ],
)
def test_upload_to_cloud_rejects_missing_or_unsupported_files(
    tmp_path,
    filename,
    error_type,
    message,
):
    page = SimpleNamespace(goto=AsyncMock(), locator=MagicMock())
    path = tmp_path / filename

    if filename == "report.csv":
        path.write_text("not an Excel file", encoding="utf-8")

    with pytest.raises(error_type, match=message):
        anyio.run(cloud_module.upload_to_cloud, page, path)

    page.goto.assert_not_awaited()


def test_orchestrator_runs_all_four_steps(monkeypatch, tmp_path):
    page = object()
    report = tmp_path / "report.xlsx"
    calls = []

    @asynccontextmanager
    async def fake_browser_session():
        yield page

    async def fake_login_crm(current_page):
        calls.append(("crm_login", current_page))

    async def fake_download(current_page):
        calls.append(("download", current_page))
        return report

    async def fake_login_cloud(current_page):
        calls.append(("cloud_login", current_page))

    async def fake_upload(current_page, file_path):
        calls.append(("upload", current_page, file_path))
        return "Upload completed. Version 1"

    monkeypatch.setattr(run_module, "browser_session", fake_browser_session)
    monkeypatch.setattr(run_module, "login_to_crm", fake_login_crm)
    monkeypatch.setattr(run_module, "download_crm_report", fake_download)
    monkeypatch.setattr(run_module, "login_to_cloud", fake_login_cloud)
    monkeypatch.setattr(run_module, "upload_to_cloud", fake_upload)

    anyio.run(run_module.run_automation)

    assert [call[0] for call in calls] == [
        "crm_login",
        "download",
        "cloud_login",
        "upload",
    ]
    assert calls[-1] == ("upload", page, report)
