from app.agent.llm_provider import get_llm
from app.agent.prompts import DIET_PLAN_PROMPT
from app.agent.state import TrainerState
from app.schemas.diet_plan import DietPlan


def design_diet_plan_node(state: TrainerState) -> dict:
    """Second step: ask the model for a diet plan that fits the calculated numbers."""
    user_profile = state["user_profile"]
    bmi_result = state["bmi_result"]

    prompt = DIET_PLAN_PROMPT.format(
        age=user_profile.age,
        gender=user_profile.gender.value,
        weight_kg=user_profile.weight_kg,
        height_cm=user_profile.height_cm,
        activity_level=user_profile.activity_level.value,
        food_preferences=", ".join(user_profile.food_preferences) or "no preferences",
        medical_conditions=", ".join(user_profile.medical_conditions) or "none",
        bmi=bmi_result.bmi,
        bmi_category=bmi_result.category,
        maintenance_calories=bmi_result.maintenance_calories,
    )

    llm = get_llm().with_structured_output(DietPlan)
    diet_plan = llm.invoke(prompt)
    return {"diet_plan": diet_plan}
