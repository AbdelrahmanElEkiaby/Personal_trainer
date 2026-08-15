"""Workout tools. They are ready but the graph does not call them yet."""

from langchain_core.tools import tool

# A very small exercise table we can replace with a real database later.
EXERCISES_BY_MUSCLE = {
    "chest": ["push up", "bench press", "chest press machine"],
    "back": ["lat pulldown", "seated row", "pull up"],
    "legs": ["squat", "leg press", "lunges"],
    "shoulders": ["shoulder press", "lateral raise", "front raise"],
    "arms": ["biceps curl", "triceps pushdown", "hammer curl"],
    "core": ["plank", "crunch", "leg raise"],
}

# Exercises we should not give to a user with this medical condition.
UNSAFE_EXERCISES_BY_CONDITION = {
    "knee pain": ["squat", "lunges", "leg press"],
    "back pain": ["deadlift", "bent over row", "good morning"],
    "shoulder pain": ["bench press", "shoulder press", "lateral raise"],
}


@tool
def get_exercises_for_muscle(muscle_name: str) -> list[str]:
    """Get a list of exercises that train the given muscle."""
    return EXERCISES_BY_MUSCLE.get(muscle_name.lower(), [])


@tool
def get_unsafe_exercises(medical_condition: str) -> list[str]:
    """Get the exercises the user must avoid because of a medical condition."""
    return UNSAFE_EXERCISES_BY_CONDITION.get(medical_condition.lower(), [])


@tool
def estimate_workout_minutes(number_of_exercises: int, sets_per_exercise: int) -> int:
    """Estimate how many minutes one workout will take."""
    minutes_per_set = 3
    return number_of_exercises * sets_per_exercise * minutes_per_set
