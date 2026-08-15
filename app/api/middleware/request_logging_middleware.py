"""Opens and closes the log trace of every HTTP request."""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware

from app.core.request_context import (
    get_request_totals,
    remember_run_info,
    start_new_request,
)
from app.observability.logger import estimate_cost_usd, log_event
from app.observability.run_log import write_run_file


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Gives every request its own id, and writes its own log file at the end."""

    async def dispatch(self, request, call_next):
        request_id = start_new_request()
        started_at = time.perf_counter()
        remember_run_info(method=request.method, path=request.url.path)

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
            # A failed run is the one we most want to read afterwards.
            remember_run_info(status_code=500, summary=get_request_totals())
            write_run_file()
            raise

        # The summary line: everything we counted while answering this request.
        totals = get_request_totals()
        summary = {
            "status_code": response.status_code,
            **totals,
            "estimated_cost_usd": estimate_cost_usd(
                totals.get("input_tokens", 0), totals.get("output_tokens", 0)
            ),
        }
        log_event(
            "api",
            "request_finished",
            details=summary,
            duration_ms=_milliseconds_since(started_at),
        )

        remember_run_info(status_code=response.status_code, summary=summary)
        run_file = write_run_file()

        response.headers["X-Request-Id"] = request_id
        if run_file:
            log_event("api", "run_file_written", details={"file": run_file})

        return response


def _milliseconds_since(started_at: float) -> int:
    return round((time.perf_counter() - started_at) * 1000)
