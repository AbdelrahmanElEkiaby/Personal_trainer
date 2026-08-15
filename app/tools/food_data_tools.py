from langchain_core.tools import tool

from app.clients import usda_client
from app.clients.usda_client import UsdaApiError


# The shortest food name we accept, so we do not search for "a" or "x".
SHORTEST_FOOD_NAME = 2


@tool
def search_foods_by_name(food_name: str) -> list[dict]:
    """Search the USDA database and return the foods that match, with their ids.

    Always call this first, then read the names and choose the food you really want.
    """
    # Guard 1: the name must be a real word, not empty and not one letter.
    food_name = food_name.strip()
    if len(food_name) < SHORTEST_FOOD_NAME:
        return [{"error": "Please give a food name with at least 2 letters."}]

    # Guard 2: the name must have at least one word that describes a food.
    if not usda_client.get_searchable_words(food_name):
        return [
            {"error": f"'{food_name}' is too general. Give a real food name like 'brown rice'."}
        ]

    try:
        results = usda_client.search_foods(food_name, how_many=5)
    except UsdaApiError as error:
        return [{"error": str(error)}]

    # Guard 3: USDA answers almost every search, so an empty list here means the
    # foods it returned had nothing to do with the name we asked for.
    if not results:
        return [{"error": f"No food named '{food_name}' was found in the USDA database."}]

    return [
        {"fdc_id": result.fdc_id, "name": result.description}
        for result in results
    ]


@tool
def get_food_nutrition_by_id(fdc_id: int, portion_grams: float = 100) -> dict:
    """Get the real calories, macros and micronutrients of one food, using its USDA id.

    Get the id from search_foods_by_name first.
    """
    try:
        nutrition = usda_client.get_food_nutrition(fdc_id, portion_grams)
    except UsdaApiError as error:
        return {"error": str(error)}

    return nutrition.model_dump()


@tool
def get_food_nutrition_facts(food_name: str, portion_grams: float = 100) -> dict:
    """Get the nutrition of a food by name, using the best match from USDA.

    This is the quick way. It is easier but less exact, because the best match is
    not always the food you meant. Use search_foods_by_name when you need to be sure.
    """
    try:
        nutrition = usda_client.find_food_nutrition(food_name, portion_grams)
    except UsdaApiError as error:
        return {"error": str(error)}

    if nutrition is None:
        return {"error": f"No food named '{food_name}' was found in the USDA database."}

    return nutrition.model_dump()


@tool
def compare_two_foods(first_food: str, second_food: str, portion_grams: float = 100) -> dict:
    """Compare the calories and the protein of two foods for the same portion.

    Use this when the user wants to know which food is the better choice.
    """
    try:
        first = usda_client.find_food_nutrition(first_food, portion_grams)
        second = usda_client.find_food_nutrition(second_food, portion_grams)
    except UsdaApiError as error:
        return {"error": str(error)}

    if first is None or second is None:
        return {"error": "One of the two foods was not found in the USDA database."}

    return {
        "portion_grams": portion_grams,
        first.food_name: {"calories": first.calories, "protein_grams": first.protein_grams},
        second.food_name: {"calories": second.calories, "protein_grams": second.protein_grams},
    }
