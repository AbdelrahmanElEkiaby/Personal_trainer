from app.agent.node_logging import log_node
from app.agent.state import TrainerState
from app.services.plan_enrichment import enrich_training_plan
from app.services.training_equipment import get_equipment_for_location


@log_node("enrich_training_plan")
def enrich_training_plan_node(state: TrainerState) -> dict:
    """Take the real exercises from ExerciseDB and check the plan is safe."""
    user_profile = state["user_profile"]
    allowed_equipment = get_equipment_for_location(user_profile.training_location)

    training_plan = enrich_training_plan(
        state["training_plan"],
        allowed_equipment,
        user_profile.medical_conditions,
    )
    return {"training_plan": training_plan}
