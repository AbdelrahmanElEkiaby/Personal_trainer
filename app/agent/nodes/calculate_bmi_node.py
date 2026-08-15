from app.agent.node_logging import log_node
from app.agent.state import TrainerState
from app.domain.body_metrics import build_bmi_result


@log_node("calculate_bmi")
def calculate_bmi_node(state: TrainerState) -> dict:
    """First step: calculate the BMI and the calories with normal Python code."""
    user_profile = state["user_profile"]
    bmi_result = build_bmi_result(user_profile)
    return {"bmi_result": bmi_result}
