from pydantic import BaseModel, Field


class Micronutrient(BaseModel):
    """One vitamin or one mineral."""

    name: str = Field(description="Name of the vitamin or the mineral")
    amount: float = Field(description="How much of it is in the portion")
    unit: str = Field(description="The unit, for example mg or ug")


class FoodSearchResult(BaseModel):
    """One food we found in the USDA database."""

    fdc_id: int = Field(description="The id USDA uses for this food")
    description: str = Field(description="The full food name from USDA")
    data_type: str = Field(description="Where the data comes from, for example SR Legacy")


class FoodNutrition(BaseModel):
    """The full nutrition of one food, already scaled to the portion we asked for."""

    fdc_id: int = Field(description="The id USDA uses for this food")
    food_name: str = Field(description="The full food name from USDA")
    portion_grams: float = Field(description="The portion these numbers are calculated for")
    calories: float = Field(description="Calories in the portion")
    protein_grams: float = Field(description="Protein in the portion")
    carbs_grams: float = Field(description="Carbohydrates in the portion")
    fat_grams: float = Field(description="Fat in the portion")
    fiber_grams: float = Field(description="Fiber in the portion")
    micronutrients: list[Micronutrient] = Field(
        default_factory=list,
        description="The vitamins and the minerals in the portion",
    )
