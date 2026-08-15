"""The use case of the app: take a user profile and return a full plan."""

from app.agent.trainer_graph import trainer_graph
from app.core.config import settings
from app.schemas.plan_response import PlanResponse
from app.schemas.user_profile import UserProfile
from app.services.log_service import log_event


def create_full_plan(user_profile: UserProfile) -> PlanResponse:
    """Run the graph and put the three results in one response."""
    # The middleware cannot read the body, so the profile is logged here.
    log_event(
        "api",
        "profile_received",
        details={
            "profile": user_profile.model_dump() if settings.log_user_details else "hidden"
        },
    )

    initial_state = {
        "user_profile": user_profile,
        "bmi_result": None,
        "diet_plan": None,
        "training_plan": None,
    }

    final_state = trainer_graph.invoke(initial_state)

    return PlanResponse(
        bmi_result=final_state["bmi_result"],
        diet_plan=final_state["diet_plan"],
        training_plan=final_state["training_plan"],
    )
