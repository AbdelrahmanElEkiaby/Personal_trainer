from pydantic import BaseModel, Field

from app.schemas.food_nutrition import Micronutrient


class FoodItem(BaseModel):
    """One food inside a meal, with its own numbers."""

    # When the model found the food with the tools it writes the id here, and then
    # the enrichment reads the exact food instead of searching by name again.
    fdc_id: str = Field(default="", description="The USDA id of this food, empty if we do not have it")
    food_name: str = Field(description="Name of the food, for example Banana")
    portion: str = Field(description="How much to eat, for example 120 g")
    # These are measured values, so they can have decimals, for example 0.2 g of fat.
    calories: float = Field(description="Calories in this portion")
    protein_grams: float = Field(description="Protein in this portion")
    carbs_grams: float = Field(description="Carbohydrates in this portion")
    fat_grams: float = Field(description="Fat in this portion")
    micronutrients: list[Micronutrient] = Field(
        description="The main vitamins and minerals in this portion"
    )


class Meal(BaseModel):
    """One meal of the day."""

    name: str = Field(description="Meal name, for example Breakfast or Snack")
    total_calories: int = Field(description="Total calories of all the foods in this meal")
    foods: list[FoodItem] = Field(description="The foods to eat in this meal")


class DietPlan(BaseModel):
    """The diet plan the model returns."""

    daily_calories: int = Field(description="Target calories per day")
    protein_grams: int = Field(description="Target protein per day in grams")
    carbs_grams: int = Field(description="Target carbohydrates per day in grams")
    fat_grams: int = Field(description="Target fat per day in grams")
    meals: list[Meal] = Field(description="The meals of a normal day")
    notes: list[str] = Field(description="Short advices, including the medical ones")
