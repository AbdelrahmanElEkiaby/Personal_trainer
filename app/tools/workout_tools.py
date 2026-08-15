from langchain_core.tools import tool

from app.services.medical_safety import get_unsafe_exercises_for


@tool
def get_unsafe_exercises(medical_condition: str) -> list[str]:
    """Get the exercises the user must avoid because of a medical condition."""
    return get_unsafe_exercises_for(medical_condition)


@tool
def estimate_workout_minutes(number_of_exercises: int, sets_per_exercise: int) -> int:
    """Estimate how many minutes one workout will take."""
    minutes_per_set = 3
    return number_of_exercises * sets_per_exercise * minutes_per_set
