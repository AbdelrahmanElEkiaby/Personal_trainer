"""The use case of the app: take a user profile and return a full plan."""

from app.agent.trainer_graph import trainer_graph
from app.schemas.plan_response import PlanResponse
from app.schemas.user_profile import UserProfile


def create_full_plan(user_profile: UserProfile) -> PlanResponse:
    """Run the graph and put the three results in one response."""
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
