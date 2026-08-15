"""Sets up the two ways we write logs.

The console gets one short readable line while the app runs. The lines themselves
are kept in memory for the request that is running, and written together into one
JSON file per run. See app/observability/run_log.py for the file itself.
"""

import logging
from datetime import datetime, timezone

from app.core.config import settings
from app.core.request_context import add_run_event

LOGGER_NAME = "trainer"


def build_log_line(record: logging.LogRecord) -> dict:
    """Turn one log record into the plain dictionary we keep and write."""
    written_at = datetime.fromtimestamp(record.created, timezone.utc)
    return {
        "timestamp": written_at.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "request_id": getattr(record, "request_id", ""),
        "level": record.levelname,
        "step": getattr(record, "step", ""),
        "event": getattr(record, "event", record.getMessage()),
        "duration_ms": getattr(record, "duration_ms", None),
        "details": getattr(record, "details", {}),
        "error": getattr(record, "error", None),
    }


class RunLogHandler(logging.Handler):
    """Keeps every line of the running request, instead of writing it right away.

    Nothing is written to disk here. The middleware writes the whole run in one
    file when the request is over, so the file is always complete and valid JSON.
    """

    def emit(self, record: logging.LogRecord) -> None:
        add_run_event(build_log_line(record))


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
    # would add the same handlers again and keep every line twice.
    if logger.handlers:
        return

    logger.addHandler(RunLogHandler())

    if settings.log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ReadableLogFormatter())
        logger.addHandler(console_handler)

    # Our lines are already complete, we do not want them repeated by the root logger.
    logger.propagate = False
