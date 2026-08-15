"""One place that collects every tool, so a node can bind them in the future."""

from app.tools.nutrition_tools import (
    calculate_daily_water_liters,
    calculate_macros_calories,
    find_food_alternatives,
)
from app.tools.workout_tools import (
    estimate_workout_minutes,
    get_exercises_for_muscle,
    get_unsafe_exercises,
)

NUTRITION_TOOLS = [
    calculate_macros_calories,
    find_food_alternatives,
    calculate_daily_water_liters,
]

WORKOUT_TOOLS = [
    get_exercises_for_muscle,
    get_unsafe_exercises,
    estimate_workout_minutes,
]

ALL_TOOLS = NUTRITION_TOOLS + WORKOUT_TOOLS
