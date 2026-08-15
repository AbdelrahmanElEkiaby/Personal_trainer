"""Remembers which request we are working on right now.

The endpoint, the graph nodes and the API clients all need the same request id,
but passing it to every function would make the code ugly. A ContextVar keeps it
in one place, and Python gives the right value to the right request by itself.
"""

import uuid
from contextvars import ContextVar
from datetime import datetime, timezone

_request_id: ContextVar[str] = ContextVar("request_id", default="")
_request_totals: ContextVar[dict | None] = ContextVar("request_totals", default=None)
# The ids the tools really showed to the model during this request.
_shown_ids: ContextVar[dict | None] = ContextVar("shown_ids", default=None)
# Every log line of this request, kept so we can write them all in one file.
_run_events: ContextVar[list | None] = ContextVar("run_events", default=None)
_run_info: ContextVar[dict | None] = ContextVar("run_info", default=None)

# The two kinds of id we remember. They live here, next to the functions that
# use them, so nothing outside has to know how the ids are stored.
FOOD_ID_KIND = "food"
EXERCISE_ID_KIND = "exercise"


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
            "input_tokens": 0,
            "output_tokens": 0,
        }
    )
    _shown_ids.set({})
    _run_events.set([])
    _run_info.set({"request_id": request_id, "started_at": datetime.now(timezone.utc)})
    return request_id


def add_run_event(one_event: dict) -> None:
    """Keep one log line, so the whole run can be written in a single file."""
    events = _run_events.get()
    if events is not None:
        events.append(one_event)


def get_run_events() -> list:
    """Every log line of this request, in the order they happened."""
    return _run_events.get() or []


def remember_run_info(**details) -> None:
    """Write down something about the run itself, like the path or the status code."""
    info = _run_info.get()
    if info is not None:
        info.update(details)


def get_run_info() -> dict:
    """What we know about this run: its id, when it started, and what was asked."""
    return _run_info.get() or {}


def remember_shown_ids(kind: str, ids: list) -> None:
    """Write down the ids a search tool really showed to the model.

    The model often invents an id that looks real instead of copying one it saw,
    so later we can refuse any id that is not in this list.
    """
    shown = _shown_ids.get()
    if shown is None:
        return
    shown.setdefault(kind, set()).update(str(one_id) for one_id in ids)


def get_shown_ids(kind: str) -> set:
    """The ids the model was really shown for this kind of thing."""
    shown = _shown_ids.get() or {}
    return shown.get(kind, set())


def remember_id_for_name(kind: str, name: str, one_id) -> None:
    """Remember which id belongs to which exact name.

    A small model cannot copy a long number, but it can copy a name. So we let it
    answer with the name, and we find the id again ourselves.
    """
    shown = _shown_ids.get()
    if shown is None:
        return
    shown.setdefault(f"{kind}_by_name", {})[name.lower().strip()] = str(one_id)


def get_id_for_name(kind: str, name: str) -> str:
    """The id of the name the tools showed, or empty when we never showed it."""
    names_we_showed = (_shown_ids.get() or {}).get(f"{kind}_by_name", {})
    name = name.lower().strip()

    if name in names_we_showed:
        return names_we_showed[name]

    # The model often writes its own label in front of the real name, like
    # "Brown rice, Flour, rice, brown". So we also accept a name that has one of
    # the names we showed inside it.
    for name_we_showed, one_id in names_we_showed.items():
        if name_we_showed in name:
            return one_id

    return ""


def get_request_id() -> str:
    """The id of the request we are working on, empty outside of a request."""
    return _request_id.get()


def count_one(what_we_counted: str) -> None:
    """Add one to a counter, for example usda_calls."""
    totals = _request_totals.get()
    if totals is not None:
        totals[what_we_counted] = totals.get(what_we_counted, 0) + 1


def count_tokens(input_tokens: int, output_tokens: int) -> None:
    """Add the tokens of one model call. With OpenAI these tokens cost money."""
    totals = _request_totals.get()
    if totals is None:
        return
    totals["input_tokens"] = totals.get("input_tokens", 0) + (input_tokens or 0)
    totals["output_tokens"] = totals.get("output_tokens", 0) + (output_tokens or 0)


def save_step_time(step_name: str, duration_ms: int) -> None:
    """Remember how long one step of the graph took."""
    totals = _request_totals.get()
    if totals is not None:
        totals["steps"][step_name] = duration_ms


def get_request_totals() -> dict:
    """Everything we counted during this request, for the summary line."""
    return _request_totals.get() or {}
