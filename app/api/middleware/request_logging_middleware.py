"""Opens and closes the log trace of every HTTP request."""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware

from app.core.request_context import get_request_totals, start_new_request
from app.services.log_service import log_event


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Gives every request its own id, and writes the first and the last line."""

    async def dispatch(self, request, call_next):
        request_id = start_new_request()
        started_at = time.perf_counter()

        log_event(
            "api",
            "request_started",
            details={"method": request.method, "path": request.url.path},
        )

        try:
            response = await call_next(request)
        except Exception as error:
            log_event(
                "api",
                "request_failed",
                duration_ms=_milliseconds_since(started_at),
                error=f"{type(error).__name__}: {error}",
                level=logging.ERROR,
            )
            raise

        # The summary line: everything we counted while answering this request.
        log_event(
            "api",
            "request_finished",
            details={"status_code": response.status_code, **get_request_totals()},
            duration_ms=_milliseconds_since(started_at),
        )

        # So the caller can find their own trace in the log file.
        response.headers["X-Request-Id"] = request_id
        return response


def _milliseconds_since(started_at: float) -> int:
    return round((time.perf_counter() - started_at) * 1000)
