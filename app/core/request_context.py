"""Remembers which request we are working on right now.

The endpoint, the graph nodes and the API clients all need the same request id,
but passing it to every function would make the code ugly. A ContextVar keeps it
in one place, and Python gives the right value to the right request by itself.
"""

import uuid
from contextvars import ContextVar

_request_id: ContextVar[str] = ContextVar("request_id", default="")
_request_totals: ContextVar[dict | None] = ContextVar("request_totals", default=None)


def start_new_request() -> str:
    """Give the new request its own id and its own empty counters."""
    request_id = uuid.uuid4().hex[:8]
    _request_id.set(request_id)
    _request_totals.set(
        {
            "steps": {},
            "llm_calls": 0,
            "llm_retries": 0,
            "usda_calls": 0,
            "exercisedb_calls": 0,
        }
    )
    return request_id


def get_request_id() -> str:
    """The id of the request we are working on, empty outside of a request."""
    return _request_id.get()


def count_one(what_we_counted: str) -> None:
    """Add one to a counter, for example usda_calls."""
    totals = _request_totals.get()
    if totals is not None:
        totals[what_we_counted] = totals.get(what_we_counted, 0) + 1


def save_step_time(step_name: str, duration_ms: int) -> None:
    """Remember how long one step of the graph took."""
    totals = _request_totals.get()
    if totals is not None:
        totals["steps"][step_name] = duration_ms


def get_request_totals() -> dict:
    """Everything we counted during this request, for the summary line."""
    return _request_totals.get() or {}
