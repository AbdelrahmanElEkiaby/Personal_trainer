"""The only functions the rest of the app uses to write a log line.

Nothing else in the app should call the logging library directly, so every line
has the same shape and the request id is never forgotten.
"""

import logging

from app.core.config import settings
from app.core.logging_config import LOGGER_NAME
from app.core.request_context import count_one, get_request_id

# We never want to write the API key in a file, it is a secret.
SECRET_PARAM_NAMES = ["api_key", "apikey", "key", "token"]


def log_event(
    step: str,
    event: str,
    details: dict | None = None,
    duration_ms: int | None = None,
    error: str | None = None,
    level: int = logging.INFO,
) -> None:
    """Write one line. `step` is where we are, `event` is what happened."""
    logging.getLogger(LOGGER_NAME).log(
        level,
        event,
        extra={
            "request_id": get_request_id(),
            "step": step,
            "event": event,
            "details": details or {},
            "duration_ms": duration_ms,
            "error": error,
        },
    )


def hide_secrets(params: dict) -> dict:
    """Replace the secret values so the API key never reaches the log file."""
    safe_params = {}
    for name, value in params.items():
        if name.lower() in SECRET_PARAM_NAMES:
            safe_params[name] = "***hidden***"
        else:
            safe_params[name] = value
    return safe_params


def log_api_call(
    step: str,
    path: str,
    params: dict,
    duration_ms: int,
    status_code: int | None = None,
    error: str | None = None,
) -> None:
    """Write one line for a call we made to an outside API."""
    count_one(f"{step}_calls")
    log_event(
        step=step,
        event="api_call_failed" if error else "api_call_finished",
        details={"path": path, "params": hide_secrets(params), "status_code": status_code},
        duration_ms=duration_ms,
        error=error,
        level=logging.WARNING if error else logging.DEBUG,
    )


def describe_value(value):
    """Turn a plan or a profile into something we can write in the log."""
    if not hasattr(value, "model_dump"):
        return value
    if settings.log_full_payloads:
        return value.model_dump()
    # When we do not want the full text, we only say which object it was.
    return {"type": type(value).__name__}
