# Personal Trainer Agent

An agent that takes the user information, calculates the BMI, then designs a diet plan
and a training plan. It is built with FastAPI, LangGraph and a local Ollama model.

## The flow

```
User profile  ->  Calculate BMI  ->  Design Diet Plan  ->  Design Training Plan
```

The BMI step is normal Python code (it is math, we do not need a model for it).
The diet plan and the training plan steps ask the local model and get back a
structured answer that Pydantic validates.

## Project structure

```
app/
  main.py                      the FastAPI app
  core/
    config.py                  settings read from the .env file
  api/
    routes/                    the URLs only
      health_router.py
      trainer_router.py
    controllers/               takes the request and calls the service
      trainer_controller.py
  services/                    the business logic
    bmi_calculator.py          all the health math
    trainer_service.py         runs the graph and builds the response
  agent/                       everything about the LangGraph agent
    state.py                   the data shared between the nodes
    llm_provider.py            creates the Ollama model
    prompts.py                 the text we send to the model
    trainer_graph.py           connects the nodes together
    nodes/
      calculate_bmi_node.py
      diet_plan_node.py
      training_plan_node.py
  schemas/                     the Pydantic models used for validation
    user_profile.py
    bmi_result.py
    diet_plan.py
    training_plan.py
    plan_response.py
  tools/                       ready for later, not called by the graph yet
    nutrition_tools.py
    workout_tools.py
    tool_registry.py
```

## How to run

1. Make sure Ollama is running and the model is downloaded:

```bash
ollama pull llama3.1:8b
```

2. Install the libraries:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. Copy the settings file:

```bash
copy .env.example .env
```

4. Start the app:

```bash
uvicorn app.main:app --reload
```

5. Open http://localhost:8000/docs and try the endpoints.

## Endpoints

| Method | URL              | What it does                                  |
| ------ | ---------------- | --------------------------------------------- |
| GET    | `/health`        | Checks the app is running and shows the model |
| POST   | `/trainer/bmi`   | Calculates the BMI only (fast, no model)      |
| POST   | `/trainer/plan`  | Calculates the BMI + diet plan + training plan |

## Example request

```json
{
  "age": 28,
  "gender": "male",
  "weight_kg": 92,
  "height_cm": 178,
  "activity_level": "lightly_active",
  "food_preferences": ["chicken", "rice", "no seafood"],
  "workout_days_per_week": 4,
  "medical_conditions": ["knee pain"]
}
```

## The tools

The files in `app/tools/` are ready but no node calls them yet. When we want the
model to use them, we bind them to the model inside the node:

```python
from app.tools.tool_registry import NUTRITION_TOOLS

llm = get_llm().bind_tools(NUTRITION_TOOLS)
```
