"""Sets up the two ways we write logs: a JSON file and a readable console line."""

import json
import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings

LOGGER_NAME = "trainer"

# We write full prompts and full plans, so the file grows fast. When it reaches
# this size we start a new one and keep the last few.
BIGGEST_FILE_BYTES = 10 * 1024 * 1024
HOW_MANY_OLD_FILES = 5


class JsonLogFormatter(logging.Formatter):
    """Writes one JSON object per line, always with the same keys."""

    def format(self, record: logging.LogRecord) -> str:
        written_at = datetime.fromtimestamp(record.created, timezone.utc)
        line = {
            "timestamp": written_at.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "request_id": getattr(record, "request_id", ""),
            "level": record.levelname,
            "step": getattr(record, "step", ""),
            "event": getattr(record, "event", record.getMessage()),
            "duration_ms": getattr(record, "duration_ms", None),
            "details": getattr(record, "details", {}),
            "error": getattr(record, "error", None),
        }
        # default=str so a date or any odd value never breaks the logging.
        return json.dumps(line, default=str)


class ReadableLogFormatter(logging.Formatter):
    """Writes one short line a human can read while the app is running."""

    def format(self, record: logging.LogRecord) -> str:
        written_at = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        duration = getattr(record, "duration_ms", None)
        duration_text = f"{duration} ms" if duration is not None else ""
        error = getattr(record, "error", None)
        error_text = f"  ERROR: {error}" if error else ""

        return (
            f"{written_at} {record.levelname:7} "
            f"[{getattr(record, 'request_id', '') or '--------'}] "
            f"{getattr(record, 'step', ''):22} "
            f"{getattr(record, 'event', ''):24} {duration_text}{error_text}"
        )


def setup_logging() -> None:
    """Prepare the logger. We call this one time when the app starts."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(settings.log_level.upper())

    # Uvicorn restarts the app when we save a file, and without this check we
    # would add the same handlers again and write every line twice.
    if logger.handlers:
        return

    log_file = Path(settings.log_file_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=BIGGEST_FILE_BYTES,
        backupCount=HOW_MANY_OLD_FILES,
        encoding="utf-8",
    )
    file_handler.setFormatter(JsonLogFormatter())
    logger.addHandler(file_handler)

    if settings.log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ReadableLogFormatter())
        logger.addHandler(console_handler)

    # Our lines are already complete, we do not want them repeated by the root logger.
    logger.propagate = False
