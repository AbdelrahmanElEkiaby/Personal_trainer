"""Nutrition tools that only need our own math, no API.

There used to be a find_food_alternatives tool here. It answered from a table of
four foods and gave back an empty list for everything else, so the model could
not tell "this food has no alternative" from "this food is not in my small
table". USDA does this job properly, so the tool was removed.
"""

from langchain_core.tools import tool

from app.domain import nutrition_math


@tool
def calculate_macros_calories(
    protein_grams: float, carbs_grams: float, fat_grams: float
) -> float:
    """Calculate how many calories come from the given grams of protein, carbs and fat."""
    return nutrition_math.calculate_macros_calories(protein_grams, carbs_grams, fat_grams)


@tool
def calculate_daily_water_liters(weight_kg: float) -> float:
    """Calculate how much water the user should drink per day, in liters."""
    return nutrition_math.calculate_daily_water_liters(weight_kg)
