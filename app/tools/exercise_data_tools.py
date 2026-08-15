from langchain_core.tools import tool

from app.clients import exercisedb_client
from app.clients.exercisedb_client import ExerciseDbError


def _to_simple_list(exercises) -> list[dict]:
    """Keep only the fields the model needs, so the answer stays short."""
    return [
        {
            "exercise_id": exercise.exercise_id,
            "name": exercise.name,
            "body_parts": exercise.body_parts,
            "target_muscles": exercise.target_muscles,
            "equipments": exercise.equipments,
            "secondary_muscles": exercise.secondary_muscles,
        }
        for exercise in exercises
    ]


@tool
def get_allowed_exercise_names() -> dict:
    """Get the body part, muscle and equipment names that ExerciseDB accepts.

    Call this first, because any other name will be refused.
    """
    try:
        return {
            "body_parts": exercisedb_client.get_body_parts(),
            "muscles": exercisedb_client.get_muscles(),
            "equipments": exercisedb_client.get_equipments(),
        }
    except ExerciseDbError as error:
        return {"error": str(error)}


@tool
def get_exercises_for_body_part(body_part: str, how_many: int = 5) -> list[dict]:
    """Get real exercises that train one body part, for example chest or upper legs.

    Use a body part name from get_allowed_exercise_names.
    """
    try:
        exercises = exercisedb_client.get_exercises_for_body_part(body_part, how_many)
    except ExerciseDbError as error:
        return [{"error": str(error)}]

    if not exercises:
        return [{"error": f"No exercise was found for the body part '{body_part}'."}]

    return _to_simple_list(exercises)


@tool
def get_exercises_for_muscle(target_muscle: str, how_many: int = 5) -> list[dict]:
    """Get real exercises that train one muscle, for example biceps or glutes.

    Use a muscle name from get_allowed_exercise_names.
    """
    try:
        exercises = exercisedb_client.get_exercises_for_muscle(target_muscle, how_many)
    except ExerciseDbError as error:
        return [{"error": str(error)}]

    if not exercises:
        return [{"error": f"No exercise was found for the muscle '{target_muscle}'."}]

    return _to_simple_list(exercises)


@tool
def get_exercises_for_equipment(equipment: str, how_many: int = 5) -> list[dict]:
    """Get real exercises that use one equipment, for example dumbbell or body weight.

    Use this when the person trains at home and has only a few equipments.
    """
    try:
        exercises = exercisedb_client.get_exercises_for_equipment(equipment, how_many)
    except ExerciseDbError as error:
        return [{"error": str(error)}]

    if not exercises:
        return [{"error": f"No exercise was found for the equipment '{equipment}'."}]

    return _to_simple_list(exercises)


@tool
def get_exercise_instructions(exercise_name: str) -> dict:
    """Get the steps that explain how to do one exercise correctly.

    Use this when the person needs to know how to perform the movement.
    """
    try:
        exercises = exercisedb_client.search_exercises_by_name(exercise_name)
    except ExerciseDbError as error:
        return {"error": str(error)}

    if not exercises:
        return {"error": f"No exercise named '{exercise_name}' was found."}

    best_match = exercises[0]
    return {
        "name": best_match.name,
        "target_muscles": best_match.target_muscles,
        "equipments": best_match.equipments,
        "instructions": best_match.instructions,
    }
