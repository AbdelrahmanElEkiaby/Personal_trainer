from app.agent.llm_provider import ask_model_for
from app.agent.node_logging import log_node
from app.agent.prompts import TRAINING_PLAN_PROMPT
from app.agent.state import TrainerState
from app.schemas.training_plan import TrainingPlan
from app.domain.training_equipment import get_equipment_for_location


@log_node("design_training_plan")
def design_training_plan_node(state: TrainerState) -> dict:
    """Third step: ask the model for a training plan that matches the diet plan."""
    user_profile = state["user_profile"]
    bmi_result = state["bmi_result"]
    diet_plan = state["diet_plan"]

    available_equipment = get_equipment_for_location(user_profile.training_location)

    prompt = TRAINING_PLAN_PROMPT.format(
        age=user_profile.age,
        gender=user_profile.gender.value,
        weight_kg=user_profile.weight_kg,
        height_cm=user_profile.height_cm,
        activity_level=user_profile.activity_level.value,
        workout_days_per_week=user_profile.workout_days_per_week,
        medical_conditions=", ".join(user_profile.medical_conditions) or "none",
        training_location=user_profile.training_location.value,
        available_equipment=", ".join(available_equipment),
        bmi=bmi_result.bmi,
        bmi_category=bmi_result.category,
        daily_calories=diet_plan.daily_calories,
        exercise_facts=state.get("exercise_facts")
        or "You have no tool data, use what you know.",
    )

    training_plan = ask_model_for(TrainingPlan, prompt)
    return {"training_plan": training_plan}
