
from __future__ import annotations

import logging
import os
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Callable, List, Optional

TOKEN_SCRUB_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9_]{30,}", re.IGNORECASE),
    re.compile(r"github_pat_[A-Za-z0-9_]{60,}", re.IGNORECASE),
    re.compile(r"gho_[A-Za-z0-9_]{30,}", re.IGNORECASE),
    re.compile(r"bearer\s+[A-Za-z0-9_\-\.]{20,}", re.IGNORECASE),
    re.compile(r"https?://[^:@\s]+:[^:@\s]+@", re.IGNORECASE),
]

def sanitize_message(msg: str) -> str:
    sanitized = msg
    for pat in TOKEN_SCRUB_PATTERNS:
        sanitized = pat.sub("[REDACTED_SECRET]", sanitized)
    return sanitized

class SensitiveSanitizingFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        record.msg = sanitize_message(str(record.msg))
        return super().format(record)

class LogStreamHandler(logging.Handler):

    def __init__(self, callback: Optional[Callable[[str], None]] = None):
        super().__init__()
        self.callback = callback
        self.history: List[str] = []
        self.max_history = 1000

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self.history.append(msg)
            if len(self.history) > self.max_history:
                self.history.pop(0)
            if self.callback:
                self.callback(msg)
        except Exception:
            self.handleError(record)

_UI_STREAM_HANDLER = LogStreamHandler()
_IS_CONFIGURED = False

def setup_logger(log_dir: Optional[Path] = None, level: int = logging.INFO) -> logging.Logger:
    global _IS_CONFIGURED
    logger = logging.getLogger("gh_bot")

    if _IS_CONFIGURED:
        return logger

    logger.setLevel(level)
    logger.propagate = False

    if log_dir is None:
        log_dir = Path(__file__).resolve().parent.parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "app.log"

    formatter = SensitiveSanitizingFormatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        str(log_file),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    _UI_STREAM_HANDLER.setFormatter(formatter)
    logger.addHandler(_UI_STREAM_HANDLER)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    _IS_CONFIGURED = True
    return logger

def get_logger() -> logging.Logger:
    if not _IS_CONFIGURED:
        return setup_logger()
    return logging.getLogger("gh_bot")

def get_ui_stream_handler() -> LogStreamHandler:
    return _UI_STREAM_HANDLER

def log_event(category: str, message: str, level: int = logging.INFO) -> None:
    logger = get_logger()
    formatted = f"[{category.upper()}] {message}"
    logger.log(level, formatted)
