from langgraph.graph import END, StateGraph

from app.agent.nodes.calculate_bmi_node import calculate_bmi_node
from app.agent.nodes.diet_plan_node import design_diet_plan_node
from app.agent.nodes.training_plan_node import design_training_plan_node
from app.agent.state import TrainerState

# Node names, kept in variables so we do not repeat the same text.
CALCULATE_BMI = "calculate_bmi"
DESIGN_DIET_PLAN = "design_diet_plan"
DESIGN_TRAINING_PLAN = "design_training_plan"


def build_trainer_graph():
    """Build the flow: user profile -> BMI -> diet plan -> training plan."""
    graph = StateGraph(TrainerState)

    graph.add_node(CALCULATE_BMI, calculate_bmi_node)
    graph.add_node(DESIGN_DIET_PLAN, design_diet_plan_node)
    graph.add_node(DESIGN_TRAINING_PLAN, design_training_plan_node)

    graph.set_entry_point(CALCULATE_BMI)
    graph.add_edge(CALCULATE_BMI, DESIGN_DIET_PLAN)
    graph.add_edge(DESIGN_DIET_PLAN, DESIGN_TRAINING_PLAN)
    graph.add_edge(DESIGN_TRAINING_PLAN, END)

    return graph.compile()


# We build the graph one time when the app starts.
trainer_graph = build_trainer_graph()
