"""The controller takes the request, calls the service and handles the errors."""

from fastapi import HTTPException

from app.schemas.plan_response import PlanResponse
from app.schemas.user_profile import UserProfile
from app.services import trainer_service


def get_full_plan(user_profile: UserProfile) -> PlanResponse:
    try:
        return trainer_service.create_full_plan(user_profile)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Could not create the plan: {error}",
        )
