"""The router only knows the URLs, the controller does the work."""

from fastapi import APIRouter

from app.api.controllers import trainer_controller
from app.schemas.bmi_result import BmiResult
from app.schemas.plan_response import PlanResponse
from app.schemas.user_profile import UserProfile

router = APIRouter(prefix="/trainer", tags=["Trainer"])


@router.post("/plan", response_model=PlanResponse)
def create_plan(user_profile: UserProfile):
    """Create the BMI, the diet plan and the training plan."""
    return trainer_controller.get_full_plan(user_profile)


@router.post("/bmi", response_model=BmiResult)
def create_bmi(user_profile: UserProfile):
    """Calculate only the BMI and the calories."""
    return trainer_controller.get_bmi(user_profile)
