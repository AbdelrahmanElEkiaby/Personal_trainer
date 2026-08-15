"""Replaces the numbers the model invented with real numbers from the APIs.

The model is good at choosing foods and exercises, but it is bad at numbers. So
after it answers, we go to USDA and to ExerciseDB, take the real values, and put
them in the plan. Then we do the additions ourselves in Python.
"""

import re

from app.clients import exercisedb_client, usda_client
from app.clients.exercisedb_client import ExerciseDbError
from app.clients.usda_client import UsdaApiError
from app.schemas.diet_plan import DietPlan
from app.schemas.training_plan import AvoidedExercise, TrainingPlan
from app.services.medical_safety import is_exercise_unsafe

# When a portion is written like "1 medium" we cannot know the grams, so we use this.
DEFAULT_PORTION_GRAMS = 100


def read_portion_grams(portion: str) -> float:
    """Read the grams out of a text like '150 g'."""
    found = re.search(r"(\d+(?:\.\d+)?)\s*g", portion.lower())
    if found:
        return float(found.group(1))
    return DEFAULT_PORTION_GRAMS


def enrich_diet_plan(diet_plan: DietPlan) -> DietPlan:
    """Put the real USDA numbers in every food, then redo all the additions."""
    foods_not_found = []

    for meal in diet_plan.meals:
        for food in meal.foods:
            portion_grams = read_portion_grams(food.portion)
            try:
                real_food = usda_client.find_food_nutrition(food.food_name, portion_grams)
            except UsdaApiError:
                real_food = None

            if real_food is None:
                foods_not_found.append(food.food_name)
                continue

            food.calories = real_food.calories
            food.protein_grams = real_food.protein_grams
            food.carbs_grams = real_food.carbs_grams
            food.fat_grams = real_food.fat_grams
            food.micronutrients = real_food.micronutrients

        # The model cannot add, so we do it.
        meal.total_calories = round(sum(food.calories for food in meal.foods))

    diet_plan.daily_calories = sum(meal.total_calories for meal in diet_plan.meals)
    diet_plan.protein_grams = round(_add_up(diet_plan, "protein_grams"))
    diet_plan.carbs_grams = round(_add_up(diet_plan, "carbs_grams"))
    diet_plan.fat_grams = round(_add_up(diet_plan, "fat_grams"))

    if foods_not_found:
        diet_plan.notes.append(
            "These foods were not found in the USDA database, so their numbers are "
            f"only an estimation: {', '.join(foods_not_found)}."
        )

    return diet_plan


def _add_up(diet_plan: DietPlan, field_name: str) -> float:
    """Add one nutrition field over every food of every meal."""
    return sum(
        getattr(food, field_name)
        for meal in diet_plan.meals
        for food in meal.foods
    )


def _find_exercise_in_exercisedb(exercise_name: str, allowed_equipment: list[str]):
    """Find the ExerciseDB exercise that fits the name and the equipment we have."""
    try:
        matches = exercisedb_client.search_exercises_by_name(exercise_name, how_many=10)
    except ExerciseDbError:
        return None

    # The model writes "Bicep Curls" but ExerciseDB writes "dumbbell bicep curl",
    # so if the full name finds nothing we try again without the last "s".
    if not matches and exercise_name.endswith("s"):
        try:
            matches = exercisedb_client.search_exercises_by_name(exercise_name[:-1], how_many=10)
        except ExerciseDbError:
            return None

    if not matches:
        return None

    # We prefer an exercise the person can really do with their equipment.
    for match in matches:
        if all(equipment in allowed_equipment for equipment in match.equipments):
            return match
    return matches[0]


def enrich_training_plan(
    training_plan: TrainingPlan,
    allowed_equipment: list[str],
    medical_conditions: list[str],
) -> TrainingPlan:
    """Put the real ExerciseDB data in every exercise and check it is safe."""
    exercises_not_found = []

    for day in training_plan.workout_days:
        for exercise in day.exercises:
            real_exercise = _find_exercise_in_exercisedb(exercise.name, allowed_equipment)
            if real_exercise is None:
                exercises_not_found.append(exercise.name)
                continue

            exercise.exercise_id = real_exercise.exercise_id
            exercise.name = real_exercise.name
            exercise.target_muscles = real_exercise.target_muscles
            exercise.equipments = real_exercise.equipments

    _check_the_plan_is_safe(training_plan, medical_conditions)

    if exercises_not_found:
        training_plan.notes.append(
            "These exercises were not found in ExerciseDB, so they have no id: "
            f"{', '.join(exercises_not_found)}."
        )

    return training_plan


def _check_the_plan_is_safe(training_plan: TrainingPlan, medical_conditions: list[str]) -> None:
    """Warn when the plan still uses an exercise that is dangerous for the person."""
    if not medical_conditions:
        return

    already_written = [avoided.exercise.lower() for avoided in training_plan.avoided_exercises]

    for day in training_plan.workout_days:
        for exercise in day.exercises:
            dangerous_because = is_exercise_unsafe(exercise.name, medical_conditions)
            if not dangerous_because or exercise.name.lower() in already_written:
                continue

            training_plan.safety_notes.append(
                f"Careful: '{exercise.name}' on day {day.day_number} can be painful "
                f"with your {dangerous_because}. Go slow, use a small weight, and stop "
                f"if it hurts."
            )
