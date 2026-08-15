"""Talks to the free ExerciseDB API and returns clean Python objects.

This API is open, it needs no key at all. It holds 1500 exercises.

Careful: if we send a filter name that the API does not know, it does not answer
with an error, it simply ignores the filter and sends all the 1500 exercises. So
we always check the filter name ourselves before we call it.
"""

import time

import httpx

from app.core.config import settings
from app.schemas.exercise_info import ExerciseInfo
from app.services.log_service import log_api_call

# The paths that give us the names the API accepts.
BODY_PARTS_PATH = "/bodyparts"
MUSCLES_PATH = "/muscles"
EQUIPMENTS_PATH = "/equipments"

# The API only understands these exact filter names, written exactly like this.
BODY_PART_FILTER = "bodyParts"
MUSCLE_FILTER = "targetMuscles"
EQUIPMENT_FILTER = "equipments"
NAME_FILTER = "name"

# The name lists never change while the app is running, so we ask only one time.
_saved_name_lists: dict[str, list[str]] = {}


class ExerciseDbError(Exception):
    """Raised when the ExerciseDB API does not answer correctly."""


def _call_exercisedb(path: str, params: dict) -> dict | list:
    """Call the API and give back what is inside the 'data' field."""
    started_at = time.perf_counter()
    try:
        response = httpx.get(
            f"{settings.exercisedb_base_url}{path}",
            params=params,
            timeout=settings.exercisedb_timeout_seconds,
        )
        response.raise_for_status()
    except httpx.HTTPError as error:
        log_api_call(
            "exercisedb",
            path,
            params,
            duration_ms=round((time.perf_counter() - started_at) * 1000),
            error=str(error),
        )
        raise ExerciseDbError(f"Could not read '{path}': {error}")

    log_api_call(
        "exercisedb",
        path,
        params,
        duration_ms=round((time.perf_counter() - started_at) * 1000),
        status_code=response.status_code,
    )
    return response.json().get("data", [])


def _to_exercise_info(raw_exercise: dict) -> ExerciseInfo:
    """Turn one raw ExerciseDB answer into our own clean object."""
    return ExerciseInfo(
        exercise_id=raw_exercise.get("exerciseId", ""),
        name=raw_exercise.get("name", ""),
        body_parts=raw_exercise.get("bodyParts", []),
        target_muscles=raw_exercise.get("targetMuscles", []),
        equipments=raw_exercise.get("equipments", []),
        secondary_muscles=raw_exercise.get("secondaryMuscles", []),
        instructions=raw_exercise.get("instructions", []),
        gif_url=raw_exercise.get("gifUrl", ""),
    )


def _get_name_list(path: str) -> list[str]:
    """Ask the API for the names it accepts, and remember them."""
    if path not in _saved_name_lists:
        answer = _call_exercisedb(path, {})
        _saved_name_lists[path] = [item["name"] for item in answer]
    return _saved_name_lists[path]


def get_body_parts() -> list[str]:
    """The body part names the API accepts, for example chest or upper legs."""
    return _get_name_list(BODY_PARTS_PATH)


def get_muscles() -> list[str]:
    """The muscle names the API accepts, for example biceps or glutes."""
    return _get_name_list(MUSCLES_PATH)


def get_equipments() -> list[str]:
    """The equipment names the API accepts, for example dumbbell or body weight."""
    return _get_name_list(EQUIPMENTS_PATH)


def _check_name_is_allowed(name: str, allowed_names: list[str], what_it_is: str) -> str:
    """Stop early if the name is not one the API knows."""
    name = name.lower().strip()
    if name not in allowed_names:
        raise ExerciseDbError(
            f"'{name}' is not a {what_it_is} the API knows. "
            f"Choose one of: {', '.join(allowed_names)}."
        )
    return name


def _get_exercises(filter_name: str, filter_value: str, how_many: int) -> list[ExerciseInfo]:
    """Ask the API for the exercises that match one filter."""
    answer = _call_exercisedb("/exercises", {filter_name: filter_value, "limit": how_many})
    return [_to_exercise_info(exercise) for exercise in answer]


def get_exercises_for_body_part(body_part: str, how_many: int = 5) -> list[ExerciseInfo]:
    """Get the exercises that train one body part, for example chest."""
    body_part = _check_name_is_allowed(body_part, get_body_parts(), "body part")
    return _get_exercises(BODY_PART_FILTER, body_part, how_many)


def get_exercises_for_muscle(target_muscle: str, how_many: int = 5) -> list[ExerciseInfo]:
    """Get the exercises that train one muscle, for example biceps."""
    target_muscle = _check_name_is_allowed(target_muscle, get_muscles(), "muscle")
    return _get_exercises(MUSCLE_FILTER, target_muscle, how_many)


def get_exercises_for_equipment(equipment: str, how_many: int = 5) -> list[ExerciseInfo]:
    """Get the exercises that use one equipment, for example dumbbell."""
    equipment = _check_name_is_allowed(equipment, get_equipments(), "equipment")
    return _get_exercises(EQUIPMENT_FILTER, equipment, how_many)


def search_exercises_by_name(exercise_name: str, how_many: int = 5) -> list[ExerciseInfo]:
    """Search the exercises by their name, for example squat."""
    exercise_name = exercise_name.lower().strip()
    if len(exercise_name) < 3:
        raise ExerciseDbError("Please give an exercise name with at least 3 letters.")
    return _get_exercises(NAME_FILTER, exercise_name, how_many)


def get_exercise_by_id(exercise_id: str) -> ExerciseInfo:
    """Get one exercise using the id ExerciseDB gave it."""
    answer = _call_exercisedb(f"/exercises/{exercise_id}", {})
    if not answer:
        raise ExerciseDbError(f"No exercise has the id '{exercise_id}'.")
    return _to_exercise_info(answer)
