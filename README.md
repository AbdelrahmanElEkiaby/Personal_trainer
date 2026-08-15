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
  clients/                     talks to the outside APIs
    usda_client.py             USDA FoodData Central
    exercisedb_client.py       ExerciseDB
  tools/                       ready for later, not called by the graph yet
    nutrition_tools.py
    food_data_tools.py         real food data from USDA
    exercise_data_tools.py     real exercises from ExerciseDB
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

| Method | URL             | What it does                                   |
| ------ | --------------- | ---------------------------------------------- |
| GET    | `/health`       | Checks the app is running and shows the model  |
| POST   | `/trainer/plan` | Calculates the BMI + diet plan + training plan |

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
  "medical_conditions": ["knee pain"],
  "training_location": "home_with_dumbbells"
}
```

`training_location` can be `gym`, `home_with_dumbbells` or `home_body_weight`.
We turn it into a list of equipment names in
`app/services/training_equipment.py`, and the training plan can only use
exercises that need one of those equipments.

## The logs

Every run writes its own file in `logs/`, named after the time it started:

```
logs/
  2026-08-15_18-47-37-831.json
  2026-08-15_18-47-48-279.json
```

One file holds one request from start to finish, so a run can be read, kept, or
compared with another run without touching the others. The milliseconds are in
the name so two runs in the same second never share a file.

Each file is a real JSON document, so `json.load()` works on it:

```json
{
  "request_id": "740d8e63",
  "started_at": "2026-08-15T18:47:48.279Z",
  "finished_at": "2026-08-15T18:47:48.284Z",
  "duration_ms": 4,
  "method": "POST",
  "path": "/trainer/plan",
  "status_code": 422,
  "summary": { "llm_calls": 0, "usda_calls": 0, "input_tokens": 0 },
  "event_count": 2,
  "events": [ ... ]
}
```

A short readable line is also printed in the terminal while the app runs.

Every event inside `events` has the same six keys:

```json
{
  "timestamp": "2026-08-15T16:25:42.575Z",
  "request_id": "1a25527e",
  "level": "INFO",
  "step": "enrich_diet_plan",
  "event": "node_finished",
  "duration_ms": 17453,
  "details": {},
  "error": null
}
```

The answer sends the id back in the `X-Request-Id` header, so you always know
which file belongs to which call.

Every file ends with a summary that says where the time went:

```json
{"event": "request_finished", "duration_ms": 94552, "details": {
  "status_code": 200,
  "steps": {"calculate_bmi": 0, "design_diet_plan": 38209, "enrich_diet_plan": 17453,
            "design_training_plan": 34377, "enrich_training_plan": 4466},
  "llm_calls": 2, "llm_retries": 0, "usda_calls": 15, "exercisedb_calls": 14}}
```

The most useful event is `food_matched`, because it writes the name we asked for
next to the name the API gave back:

```json
{"event": "food_matched", "details": {
  "asked": "Baked salmon", "matched": "Fish oil, salmon",
  "calories_before": 180.0, "calories_after": 1082.4}}
```

### Settings

| Setting              | What it does                                          |
| -------------------- | ----------------------------------------------------- |
| `LOG_LEVEL`          | `DEBUG` also writes every USDA and ExerciseDB call    |
| `LOG_FOLDER`         | Where the run files are written                       |
| `LOG_TO_CONSOLE`     | Turn the readable terminal lines off                  |
| `LOG_FULL_PAYLOADS`  | Write the full prompts and the full plans             |
| `LOG_USER_DETAILS`   | Write the profile, which has the medical conditions   |

The API key is never written, and `logs/` is in `.gitignore`.

## The tools

The files in `app/tools/` are ready but no node calls them yet. When we want the
model to use them, we bind them to the model inside the node:

```python
from app.tools.tool_registry import FOOD_DATA_TOOLS

llm = get_llm().bind_tools(FOOD_DATA_TOOLS)
```

## Real food data (USDA)

`app/clients/usda_client.py` reads the real nutrition of any food from the
USDA FoodData Central database: calories, protein, carbs, fat, fiber and 14
micronutrients (Calcium, Iron, Magnesium, Phosphorus, Potassium, Sodium, Zinc,
Vitamin A, C, D, E, K, B6 and B12).

USDA always gives the numbers for 100 grams, so the client scales them to the
portion we ask for.

### The API key

`DEMO_KEY` works out of the box but it only allows **30 requests per hour**.
Get a free key from https://fdc.nal.usda.gov/api-key-signup.html and put it in
the `.env` file:

```
USDA_API_KEY=your_key_here
```

### Important: search twice before you trust a result

The first search result is not always the food you meant. Searching for
`banana` returns the dried banana powder first, and that has about 3 times the
calories of a fresh banana. So the correct way is two steps:

```python
# 1. Look at the matches and their ids
search_foods_by_name("banana")
# -> [{"fdc_id": 1105314, "name": "Bananas, ripe and slightly ripe, raw"}, ...]

# 2. Ask for the one you really want
get_food_nutrition_by_id(fdc_id=1105314, portion_grams=120)
```

`get_food_nutrition_facts(food_name)` does both steps in one call. It is easier
but it trusts the first match, so only use it when the food name is very clear.

### The guard on the search

USDA answers almost every search, even a search that makes no sense. Searching
for `zzzzqqq not a food` used to return Oats, only because the word "food" is
inside "Oats (Includes foods for USDA's Food Distribution Program)".

So `search_foods_by_name` now checks three things:

1. The name is not empty and has at least 2 letters.
2. The name has at least one word that really describes a food. Words like
   "food", "raw" or "fresh" are too common to count.
3. Every result USDA sends back must contain one of those words, if not we drop it.

When nothing survives the check, the tool answers with a clear error instead of
a wrong food.

## Real exercises (ExerciseDB)

`app/clients/exercisedb_client.py` reads real exercises from ExerciseDB. Every
exercise comes with its name, body part, target muscle, equipment, the secondary
muscles it also trains, and the steps that explain how to do it.

### No API key needed

We use the free and open host, `https://oss.exercisedb.dev/api/v1`. It needs no
key and no sign up, and it holds 1500 exercises.

The paid host adds bigger GIFs and a difficulty level, but the free one already
gives everything our training plan needs.

### The names ExerciseDB accepts

ExerciseDB only knows 10 body parts, 50 muscles and 28 equipments. "legs" is not
a body part, the correct name is "upper legs".

This matters a lot, because when we send a name the API does not know, **it does
not answer with an error**. It quietly ignores our filter and sends all the 1500
exercises. So asking for "muscles=biceps" instead of "targetMuscles=biceps"
gives back chest and back exercises, and nothing tells us something went wrong.

To stay safe:

- The client asks the API one time for the allowed names and keeps them.
- Every filter name is checked against that list before we call the API.
- `get_allowed_exercise_names` gives the model the full list of names it can use.
