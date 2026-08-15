"""One place that collects every tool, so a node can bind them in the future."""

from app.tools.exercise_data_tools import (
    get_allowed_exercise_names,
    get_exercise_instructions,
    get_exercises_for_body_part,
    get_exercises_for_equipment,
    get_exercises_for_muscle,
)
from app.tools.food_data_tools import (
    compare_two_foods,
    get_food_nutrition_by_id,
    get_food_nutrition_facts,
    search_foods_by_name,
)
from app.tools.nutrition_tools import (
    calculate_daily_water_liters,
    calculate_macros_calories,
    find_food_alternatives,
)
from app.tools.workout_tools import estimate_workout_minutes, get_unsafe_exercises

# Tools that only use our own simple math and tables.
NUTRITION_TOOLS = [
    calculate_macros_calories,
    find_food_alternatives,
    calculate_daily_water_liters,
]

# Tools that bring real food data from the USDA database.
FOOD_DATA_TOOLS = [
    search_foods_by_name,
    get_food_nutrition_by_id,
    get_food_nutrition_facts,
    compare_two_foods,
]

# Tools that bring real exercises from ExerciseDB.
EXERCISE_DATA_TOOLS = [
    get_allowed_exercise_names,
    get_exercises_for_body_part,
    get_exercises_for_muscle,
    get_exercises_for_equipment,
    get_exercise_instructions,
]

# Tools that use our own simple tables.
WORKOUT_TOOLS = [
    get_unsafe_exercises,
    estimate_workout_minutes,
]

ALL_TOOLS = NUTRITION_TOOLS + FOOD_DATA_TOOLS + EXERCISE_DATA_TOOLS + WORKOUT_TOOLS
