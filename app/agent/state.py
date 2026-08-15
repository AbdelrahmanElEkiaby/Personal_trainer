from typing import Optional, TypedDict

from app.schemas.bmi_result import BmiResult
from app.schemas.diet_plan import DietPlan
from app.schemas.training_plan import TrainingPlan
from app.schemas.user_profile import UserProfile


class TrainerState(TypedDict):
    """The data that travels between the graph nodes.

    Every node reads what it needs and adds its own result.
    """

    user_profile: UserProfile
    bmi_result: Optional[BmiResult]
    # What the model found with the tools before it designed each plan.
    food_facts: str
    exercise_facts: str
    diet_plan: Optional[DietPlan]
    training_plan: Optional[TrainingPlan]
