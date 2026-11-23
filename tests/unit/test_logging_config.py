from __future__ import annotations

import logging

import pytest

from crm_cloud_demo import logging_config


def test_configure_logging_creates_console_and_rotating_file_handlers(
    tmp_path,
    monkeypatch,
):
    logger = logging.getLogger(logging_config.LOGGER_NAME)
    previous_handlers = list(logger.handlers)
    previous_level = logger.level
    previous_propagate = logger.propagate

    for handler in previous_handlers:
        logger.removeHandler(handler)

    monkeypatch.setattr(logging_config, "PROJECT_ROOT", tmp_path)
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    try:
        configured = logging_config.configure_logging()
        assert configured is logger
        assert configured.level == logging.DEBUG
        assert len(configured.handlers) == 2

        configured.info("test log entry")
        for handler in configured.handlers:
            handler.flush()

        log_file = tmp_path / "logs" / "automation.log"
        assert log_file.is_file()
        assert "test log entry" in log_file.read_text(encoding="utf-8")

        assert logging_config.configure_logging() is logger
        assert len(configured.handlers) == 2
    finally:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()

        for handler in previous_handlers:
            logger.addHandler(handler)

        logger.setLevel(previous_level)
        logger.propagate = previous_propagate


def test_log_configuration_rejects_unknown_level(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "NOT_A_LEVEL")
    with pytest.raises(ValueError, match="Nível de log inválido"):
        logging_config._get_log_level()
