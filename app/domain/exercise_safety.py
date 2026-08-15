"""Knows which exercises are dangerous for which medical condition.

Pure rules: this file reads nothing, calls nothing, and answers the same way
every time.
"""

# Exercises we should not give to a user with this medical condition.
UNSAFE_EXERCISES_BY_CONDITION = {
    "knee pain": ["squat", "lunge", "leg press", "jump", "deep squat"],
    "back pain": ["deadlift", "bent over row", "good morning", "sit-up"],
    "shoulder pain": ["bench press", "shoulder press", "lateral raise", "upright row"],
    "high blood pressure": ["deadlift", "overhead press", "handstand"],
}


def get_unsafe_exercises_for(medical_condition: str) -> list[str]:
    """Give the exercises the person must avoid for one condition."""
    return UNSAFE_EXERCISES_BY_CONDITION.get(medical_condition.lower().strip(), [])


def is_exercise_unsafe(exercise_name: str, medical_conditions: list[str]) -> str:
    """Say which condition makes this exercise dangerous, or an empty text if it is safe."""
    exercise_name = exercise_name.lower()
    for condition in medical_conditions:
        for unsafe_word in get_unsafe_exercises_for(condition):
            if unsafe_word in exercise_name:
                return condition
    return ""
