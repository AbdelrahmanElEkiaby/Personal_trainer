"""Talks to the USDA FoodData Central API and returns clean Python objects.

The API gives every number for 100 grams of the food, so we scale the numbers
ourselves to the portion the user asked for.
"""

import time

import httpx

from app.core.config import settings
from app.schemas.food_nutrition import FoodNutrition, FoodSearchResult, Micronutrient
from app.services.log_service import log_api_call

# USDA gives every nutrient a number. These are the ones we care about.
CALORIES_NUMBER = "208"
# Some foods store the calories under these numbers instead of 208.
BACKUP_CALORIES_NUMBERS = ["957", "958"]

MACRO_NUTRIENT_NUMBERS = {
    "203": "protein_grams",
    "204": "fat_grams",
    "205": "carbs_grams",
    "291": "fiber_grams",
}

MICRO_NUTRIENT_NAMES = {
    "301": "Calcium",
    "303": "Iron",
    "304": "Magnesium",
    "305": "Phosphorus",
    "306": "Potassium",
    "307": "Sodium",
    "309": "Zinc",
    "401": "Vitamin C",
    "415": "Vitamin B6",
    "418": "Vitamin B12",
    "318": "Vitamin A",
    "323": "Vitamin E",
    "328": "Vitamin D",
    "430": "Vitamin K",
}

# The USDA numbers are always for 100 grams.
USDA_PORTION_GRAMS = 100

# These two sources hold simple foods like rice or chicken, not branded products.
GENERIC_FOOD_TYPES = "Foundation,SR Legacy"

# USDA answers almost every search, even a search that makes no sense. Searching for
# "zzzzqqq not a food" returns Oats, only because the word "food" is inside
# "Oats (Includes foods for USDA's Food Distribution Program)".
# So these words are too common to prove that a result is really the food we asked for.
TOO_COMMON_WORDS = {
    "food", "foods", "raw", "fresh", "cooked", "plain", "with", "without",
    "and", "the", "not", "for", "from", "meat", "some", "any",
}

# A word shorter than this is ignored when we check the results.
SHORTEST_USEFUL_WORD = 3


class UsdaApiError(Exception):
    """Raised when the USDA API does not answer correctly."""


def _build_params(extra_params: dict) -> dict:
    """Every request needs the api key, so we add it in one place."""
    params = {"api_key": settings.usda_api_key}
    params.update(extra_params)
    return params


def _call_usda(path: str, extra_params: dict, what_we_wanted: str) -> dict:
    """Call USDA one time, write the log line, and give back the answer."""
    started_at = time.perf_counter()
    try:
        response = httpx.get(
            f"{settings.usda_base_url}{path}",
            params=_build_params(extra_params),
            timeout=settings.usda_timeout_seconds,
        )
        response.raise_for_status()
    except httpx.HTTPError as error:
        log_api_call(
            "usda",
            path,
            extra_params,
            duration_ms=round((time.perf_counter() - started_at) * 1000),
            error=str(error),
        )
        raise UsdaApiError(f"Could not {what_we_wanted}: {error}")

    log_api_call(
        "usda",
        path,
        extra_params,
        duration_ms=round((time.perf_counter() - started_at) * 1000),
        status_code=response.status_code,
    )
    return response.json()


def get_searchable_words(food_name: str) -> list[str]:
    """Keep only the words that really describe the food we are looking for."""
    words = food_name.lower().replace(",", " ").replace("-", " ").split()
    return [
        word
        for word in words
        if len(word) >= SHORTEST_USEFUL_WORD and word not in TOO_COMMON_WORDS
    ]


def is_really_the_food(description: str, searchable_words: list[str]) -> bool:
    """Check that the food USDA returned has something to do with what we searched."""
    # If the search had no useful word, we cannot check anything, so we keep the result.
    if not searchable_words:
        return True

    description = description.lower()
    return any(word in description for word in searchable_words)


def search_foods(food_name: str, how_many: int = 5) -> list[FoodSearchResult]:
    """Search the USDA database and return the foods that really match the name.

    USDA answers almost every search, so we drop the results that have nothing to
    do with the food we asked for.
    """
    answer = _call_usda(
        "/foods/search",
        {"query": food_name, "dataType": GENERIC_FOOD_TYPES, "pageSize": how_many},
        f"search for '{food_name}'",
    )

    foods = answer.get("foods", [])
    searchable_words = get_searchable_words(food_name)

    return [
        FoodSearchResult(
            fdc_id=food["fdcId"],
            description=food["description"],
            data_type=food["dataType"],
        )
        for food in foods
        if is_really_the_food(food["description"], searchable_words)
    ]


def get_food_nutrition(fdc_id: int, portion_grams: float = 100) -> FoodNutrition:
    """Get the full nutrition of one food, scaled to the portion we want."""
    food = _call_usda(f"/food/{fdc_id}", {}, f"read the food {fdc_id}")
    scale = portion_grams / USDA_PORTION_GRAMS

    calories = 0.0
    # Some USDA foods have no calories at all. Saying 0 would be a lie, so we
    # remember whether we really found the value.
    calories_were_found = False
    macros = {"protein_grams": 0.0, "fat_grams": 0.0, "carbs_grams": 0.0, "fiber_grams": 0.0}
    micronutrients = []

    for entry in food.get("foodNutrients", []):
        nutrient = entry.get("nutrient", {})
        number = nutrient.get("number")
        amount = entry.get("amount")

        # Some rows are only titles and have no amount, so we skip them.
        if amount is None:
            continue

        if number == CALORIES_NUMBER:
            calories = amount * scale
            calories_were_found = True
        elif number in BACKUP_CALORIES_NUMBERS and not calories_were_found:
            calories = amount * scale
            calories_were_found = True
        elif number in MACRO_NUTRIENT_NUMBERS:
            macros[MACRO_NUTRIENT_NUMBERS[number]] = amount * scale
        elif number in MICRO_NUTRIENT_NAMES:
            micronutrients.append(
                Micronutrient(
                    name=MICRO_NUTRIENT_NAMES[number],
                    amount=round(amount * scale, 2),
                    unit=nutrient.get("unitName", ""),
                )
            )

    # Better to say we do not know than to answer 0 calories for a real food.
    if not calories_were_found:
        raise UsdaApiError(
            f"USDA has no calories for '{food.get('description', fdc_id)}'."
        )

    return FoodNutrition(
        fdc_id=food["fdcId"],
        food_name=food["description"],
        portion_grams=portion_grams,
        calories=round(calories, 1),
        protein_grams=round(macros["protein_grams"], 1),
        carbs_grams=round(macros["carbs_grams"], 1),
        fat_grams=round(macros["fat_grams"], 1),
        fiber_grams=round(macros["fiber_grams"], 1),
        micronutrients=micronutrients,
    )


def find_food_nutrition(food_name: str, portion_grams: float = 100) -> FoodNutrition | None:
    """Search for a food by name and return the nutrition of the best match."""
    results = search_foods(food_name, how_many=1)
    if not results:
        return None
    return get_food_nutrition(results[0].fdc_id, portion_grams)
