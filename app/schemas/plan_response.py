from pydantic import BaseModel

from app.schemas.bmi_result import BmiResult
from app.schemas.diet_plan import DietPlan
from app.schemas.training_plan import TrainingPlan


class PlanResponse(BaseModel):
    """What the API sends back to the user."""

    bmi_result: BmiResult
    diet_plan: DietPlan
    training_plan: TrainingPlan
