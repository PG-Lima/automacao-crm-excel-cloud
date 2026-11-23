from __future__ import annotations

import asyncio
import hashlib
import logging
import socket
import threading
import time
from dataclasses import replace
from io import BytesIO

import pytest
import uvicorn
from openpyxl import load_workbook

from crm_cloud_demo import config, logging_config
from crm_cloud_demo.apps.cloud import storage as cloud_storage
from crm_cloud_demo.apps.crm import routes as crm_routes
from crm_cloud_demo.automation import cloud as automation_cloud
from crm_cloud_demo.automation import crm as automation_crm
from crm_cloud_demo.automation.run import run_automation

pytestmark = pytest.mark.e2e


def _free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def _start_server(app, port: int) -> tuple[uvicorn.Server, threading.Thread]:
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host="127.0.0.1",
            port=port,
            log_level="error",
            access_log=False,
        )
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    deadline = time.monotonic() + 20
    while not server.started and thread.is_alive() and time.monotonic() < deadline:
        time.sleep(0.05)

    if not server.started:
        server.should_exit = True
        thread.join(timeout=5)
        raise RuntimeError(f"Local demo server failed to start on port {port}.")

    return server, thread


def test_real_playwright_workflow_moves_report_from_crm_to_cloud_library(
    tmp_path,
    monkeypatch,
):
    crm_port = _free_port()
    cloud_port = _free_port()

    test_settings = replace(
        config.settings,
        crm_base_url=f"http://127.0.0.1:{crm_port}",
        cloud_base_url=f"http://127.0.0.1:{cloud_port}",
        storage_path=tmp_path / "storage",
        database_path=tmp_path / "storage" / "metadata.db",
        playwright_headless=True,
    )

    monkeypatch.setattr(config, "settings", test_settings)
    monkeypatch.setattr(crm_routes, "settings", test_settings)
    monkeypatch.setattr(cloud_storage, "settings", test_settings)
    monkeypatch.setattr(automation_crm, "settings", test_settings)
    monkeypatch.setattr(automation_cloud, "settings", test_settings)
    monkeypatch.setattr(automation_crm, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(logging_config, "PROJECT_ROOT", tmp_path)

    from crm_cloud_demo.apps.cloud.app import app as cloud_app
    from crm_cloud_demo.apps.crm.app import app as crm_app

    running_servers: list[tuple[uvicorn.Server, threading.Thread]] = []

    try:
        running_servers.append(_start_server(crm_app, crm_port))
        running_servers.append(_start_server(cloud_app, cloud_port))

        asyncio.run(run_automation())

        downloads = list((tmp_path / "downloads").glob("*.xlsx"))
        assert len(downloads) == 1
        report_bytes = downloads[0].read_bytes()
        assert report_bytes

        workbook = load_workbook(BytesIO(report_bytes), read_only=True, data_only=True)
        assert workbook.sheetnames == ["Negociações", "Resumo"]
        assert workbook["Negociações"].max_row > 1
        workbook.close()

        documents = cloud_storage.list_documents()
        assert len(documents) == 1

        uploaded = documents[0]
        stored_path = test_settings.storage_path / "uploads" / uploaded["stored_filename"]
        assert stored_path.is_file()
        assert uploaded["sha256"] == hashlib.sha256(stored_path.read_bytes()).hexdigest()
        assert uploaded["sha256"] == hashlib.sha256(report_bytes).hexdigest()
        assert uploaded["version"] == 1
        assert uploaded["original_filename"] == downloads[0].name

        log_file = tmp_path / "logs" / "automation.log"
        log_content = log_file.read_text(encoding="utf-8")
        assert "Iniciando automação." in log_content
        assert "Login no CRM realizado." in log_content
        assert "Login na biblioteca realizado." in log_content
        assert "Automação finalizada com sucesso." in log_content
        assert test_settings.crm_demo_password not in log_content
        assert test_settings.cloud_demo_password not in log_content
    finally:
        for server, thread in reversed(running_servers):
            server.should_exit = True
            thread.join(timeout=15)

        logger = logging.getLogger(logging_config.LOGGER_NAME)
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()
        logger.propagate = True
