from app.agent.node_logging import log_node
from app.agent.prompts import GATHER_EXERCISE_FACTS_PROMPT
from app.agent.state import TrainerState
from app.agent.tool_loop import collect_facts_with_tools, write_facts_for_the_prompt
from app.domain.training_equipment import get_equipment_for_location
from app.tools.tool_registry import EXERCISE_DATA_TOOLS


@log_node("gather_exercise_facts")
def gather_exercise_facts_node(state: TrainerState) -> dict:
    """Let the model use the ExerciseDB tools before it writes the training plan."""
    user_profile = state["user_profile"]
    available_equipment = get_equipment_for_location(user_profile.training_location)

    prompt = GATHER_EXERCISE_FACTS_PROMPT.format(
        training_location=user_profile.training_location.value,
        available_equipment=", ".join(available_equipment),
        medical_conditions=", ".join(user_profile.medical_conditions) or "none",
        workout_days_per_week=user_profile.workout_days_per_week,
    )

    facts_found = collect_facts_with_tools(
        EXERCISE_DATA_TOOLS, prompt, "gather_exercise_facts"
    )
    return {"exercise_facts": write_facts_for_the_prompt(facts_found)}
