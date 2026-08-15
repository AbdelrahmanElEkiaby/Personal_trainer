from langchain_core.tools import tool

from app.clients import usda_client
from app.clients.usda_client import UsdaApiError
from app.core.request_context import (
    FOOD_ID_KIND,
    get_shown_ids,
    remember_id_for_name,
    remember_shown_ids,
)

# How many foods we fully read for one search. Every one costs an extra API call,
# so we keep it small.
HOW_MANY_FOODS_WE_READ = 3


# The shortest food name we accept, so we do not search for "a" or "x".
SHORTEST_FOOD_NAME = 2


@tool
def search_foods_by_name(food_name: str) -> list[dict]:
    """Search the USDA database and return the matching foods with their real nutrition.

    This is the only tool you need for a food. It already gives you the calories
    and the macros for 100 g, so read the names, choose the plain food you want,
    and copy its name exactly into your plan.
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

    # We write down the ids we showed, so we can refuse an invented one later.
    remember_shown_ids(FOOD_ID_KIND, [result.fdc_id for result in results])

    # We read the real nutrition here, so the model never has to copy an id.
    # It only has to copy the name, and we find the id again ourselves.
    foods_with_nutrition = []
    for result in results[:HOW_MANY_FOODS_WE_READ]:
        remember_id_for_name(FOOD_ID_KIND, result.description, result.fdc_id)
        try:
            nutrition = usda_client.get_food_nutrition(result.fdc_id, 100)
        except UsdaApiError:
            # USDA has no numbers for this food, so it is not useful for a plan.
            continue

        foods_with_nutrition.append(
            {
                "name": result.description,
                "per_100_grams": {
                    "calories": nutrition.calories,
                    "protein_grams": nutrition.protein_grams,
                    "carbs_grams": nutrition.carbs_grams,
                    "fat_grams": nutrition.fat_grams,
                },
            }
        )

    if not foods_with_nutrition:
        return [{"error": f"USDA has no nutrition numbers for '{food_name}'."}]

    return foods_with_nutrition


@tool
def get_food_nutrition_by_id(fdc_id: int, portion_grams: float = 100) -> dict:
    """Get the real calories, macros and micronutrients of one food, using its USDA id.

    Get the id from search_foods_by_name first.
    """
    # The model likes to invent an id that looks real. Those ids exist in USDA,
    # so they answer normally and we would get a completely different food. We
    # only accept an id that a search really showed.
    ids_we_showed = get_shown_ids(FOOD_ID_KIND)
    if str(fdc_id) not in ids_we_showed:
        return {
            "error": (
                f"The id {fdc_id} did not come from a search, so it is probably the "
                f"wrong food. Call search_foods_by_name first and use one of the ids "
                f"it gives you."
            ),
            "ids_you_can_use": sorted(ids_we_showed),
        }

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
