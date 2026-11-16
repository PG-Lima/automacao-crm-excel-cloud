from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler

from .config import PROJECT_ROOT

LOGGER_NAME = "crm_cloud_demo"
DEFAULT_LOG_LEVEL = "INFO"
MAX_LOG_BYTES = 1_000_000
BACKUP_COUNT = 3


def _get_log_level() -> int:
    level_name = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL).strip().upper()
    level = getattr(logging, level_name, None)

    if not isinstance(level, int):
        raise ValueError(f"Nível de log inválido: {level_name}")

    return level


def configure_logging() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    log_level = _get_log_level()

    logger.setLevel(log_level)
    logger.propagate = False

    # Evita adicionar os mesmos handlers várias vezes.
    if logger.handlers:
        return logger

    log_directory = PROJECT_ROOT / "logs"
    log_directory.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Exibe os registros no terminal.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # Armazena os registros em arquivo com rotação automática.
    file_handler = RotatingFileHandler(
        log_directory / "automation.log",
        maxBytes=MAX_LOG_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
