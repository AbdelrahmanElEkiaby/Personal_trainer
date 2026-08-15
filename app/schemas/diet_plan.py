from pydantic import BaseModel, Field


class Meal(BaseModel):
    name: str = Field(description="Meal name, for example Breakfast or Snack")
    foods: list[str] = Field(description="Foods to eat in this meal with their portions")
    calories: int = Field(description="Total calories of this meal")


class DietPlan(BaseModel):
    """The diet plan the model returns."""

    daily_calories: int = Field(description="Target calories per day")
    protein_grams: int = Field(description="Target protein per day in grams")
    carbs_grams: int = Field(description="Target carbohydrates per day in grams")
    fat_grams: int = Field(description="Target fat per day in grams")
    meals: list[Meal] = Field(description="The meals of a normal day")
    notes: list[str] = Field(description="Short advices, including the medical ones")
