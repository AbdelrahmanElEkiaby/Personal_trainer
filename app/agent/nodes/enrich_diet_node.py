from app.agent.node_logging import log_node
from app.agent.state import TrainerState
from app.services.plan_enrichment import enrich_diet_plan


@log_node("enrich_diet_plan")
def enrich_diet_plan_node(state: TrainerState) -> dict:
    """Take the real food numbers from USDA and redo the additions."""
    diet_plan = enrich_diet_plan(state["diet_plan"])
    return {"diet_plan": diet_plan}
