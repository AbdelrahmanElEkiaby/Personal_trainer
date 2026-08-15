from app.agent.node_logging import log_node
from app.agent.prompts import GATHER_FOOD_FACTS_PROMPT
from app.agent.state import TrainerState
from app.agent.tool_loop import collect_facts_with_tools, write_facts_for_the_prompt
from app.tools.tool_registry import FOOD_DATA_TOOLS


@log_node("gather_food_facts")
def gather_food_facts_node(state: TrainerState) -> dict:
    """Let the model use the USDA tools before it writes the diet plan."""
    user_profile = state["user_profile"]
    bmi_result = state["bmi_result"]

    prompt = GATHER_FOOD_FACTS_PROMPT.format(
        food_preferences=", ".join(user_profile.food_preferences) or "no preferences",
        medical_conditions=", ".join(user_profile.medical_conditions) or "none",
        maintenance_calories=bmi_result.maintenance_calories,
    )

    facts_found = collect_facts_with_tools(FOOD_DATA_TOOLS, prompt, "gather_food_facts")
    return {"food_facts": write_facts_for_the_prompt(facts_found)}
