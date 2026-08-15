from pydantic import BaseModel, Field


class BmiResult(BaseModel):
    """The numbers we calculate ourselves, without asking the model."""

    bmi: float = Field(description="Body Mass Index value")
    category: str = Field(description="Underweight, Normal weight, Overweight or Obese")
    bmr_calories: int = Field(description="Calories the body burns at complete rest")
    maintenance_calories: int = Field(description="Calories needed to keep the current weight")
