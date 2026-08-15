"""The small nutrition calculations: calories from macros, and daily water.

Pure rules, so both the tools and the enrichment can use the same functions.
"""

# Calories that one gram of each macro nutrient gives.
CALORIES_PER_GRAM = {"protein": 4, "carbs": 4, "fat": 9}

# Millilitres of water per kilogram of body weight, per day.
WATER_ML_PER_KG = 33


def calculate_macros_calories(
    protein_grams: float, carbs_grams: float, fat_grams: float
) -> float:
    """How many calories these grams of protein, carbs and fat give."""
    return (
        protein_grams * CALORIES_PER_GRAM["protein"]
        + carbs_grams * CALORIES_PER_GRAM["carbs"]
        + fat_grams * CALORIES_PER_GRAM["fat"]
    )


def calculate_daily_water_liters(weight_kg: float) -> float:
    """How many liters of water the person should drink in one day."""
    return round(weight_kg * WATER_ML_PER_KG / 1000, 1)
