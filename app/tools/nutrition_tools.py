"""Nutrition tools. They are ready but the graph does not call them yet."""

from langchain_core.tools import tool

# Calories of one gram of each macro nutrient.
CALORIES_PER_GRAM = {"protein": 4, "carbs": 4, "fat": 9}

# A very small food table we can replace with a real database later.
FOOD_ALTERNATIVES = {
    "chicken breast": ["turkey breast", "white fish", "tofu"],
    "rice": ["potato", "pasta", "quinoa"],
    "milk": ["almond milk", "soy milk", "lactose free milk"],
    "eggs": ["egg whites", "greek yogurt", "cottage cheese"],
}


@tool
def calculate_macros_calories(protein_grams: int, carbs_grams: int, fat_grams: int) -> int:
    """Calculate how many calories come from the given grams of protein, carbs and fat."""
    protein_calories = protein_grams * CALORIES_PER_GRAM["protein"]
    carbs_calories = carbs_grams * CALORIES_PER_GRAM["carbs"]
    fat_calories = fat_grams * CALORIES_PER_GRAM["fat"]
    return protein_calories + carbs_calories + fat_calories


@tool
def find_food_alternatives(food_name: str) -> list[str]:
    """Find other foods the user can eat instead of the given food."""
    return FOOD_ALTERNATIVES.get(food_name.lower(), [])


@tool
def calculate_daily_water_liters(weight_kg: float) -> float:
    """Calculate how much water the user should drink per day, in liters."""
    return round(weight_kg * 0.033, 1)
