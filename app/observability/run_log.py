"""Writes one JSON file for every run, named after the time the run started.

One file holds everything that happened during one request, so a run can be read,
kept, or compared with another run without touching the others.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings
from app.core.request_context import get_run_events, get_run_info



def build_file_name(started_at: datetime) -> str:
    """The name of the file for a run that started at this time.

    Windows does not allow ":" in a file name, so the time uses dashes. The
    milliseconds are there so two runs in the same second never share a name.
    """
    return started_at.strftime("%Y-%m-%d_%H-%M-%S-") + f"{started_at.microsecond // 1000:03d}.json"


def write_run_file() -> str:
    """Write everything this run logged into one JSON file. Returns the path."""
    events = get_run_events()
    if not events:
        return ""

    run_info = get_run_info()
    started_at = run_info.get("started_at") or datetime.now(timezone.utc)
    finished_at = datetime.now(timezone.utc)

    document = {
        "request_id": run_info.get("request_id", ""),
        "started_at": started_at.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "finished_at": finished_at.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "duration_ms": round((finished_at - started_at).total_seconds() * 1000),
        "method": run_info.get("method", ""),
        "path": run_info.get("path", ""),
        "status_code": run_info.get("status_code"),
        "summary": run_info.get("summary", {}),
        "event_count": len(events),
        "events": events,
    }

    folder = Path(settings.log_folder)
    folder.mkdir(parents=True, exist_ok=True)
    run_file = folder / build_file_name(started_at)

    # default=str so an odd value can never stop us from writing the file.
    run_file.write_text(
        json.dumps(document, indent=2, default=str, ensure_ascii=False),
        encoding="utf-8",
    )
    return str(run_file)
