# Personal Trainer Agent

Takes a person's body data and returns a diet plan and a training plan.

Built with FastAPI, LangGraph, and OpenAI or a local Ollama model.

## How it works

```
BMI -> find foods -> diet plan -> check
    -> find exercises -> training plan -> check
```

The BMI is plain Python. The model finds real foods and exercises with the tools,
then designs each plan. The check steps read the real numbers back from USDA and
ExerciseDB and redo the maths.

The model chooses. The code counts.

## Run it

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Put your OpenAI key in `.env`. To use the local model instead, set
`LLM_PROVIDER=ollama` and run `ollama pull llama3.1:8b`.

Then open http://localhost:8000/docs.

## Frontend

A small React form that calls the API and shows the plan. It lives in
`frontend/` and needs the backend running in another terminal.

```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173.

```
frontend/
  index.html          the empty page React fills
  src/main.jsx        starts React
  src/App.jsx         the form, the fetch, the loading and error state
  src/PlanResult.jsx  shows the BMI, the diet plan and the training plan
  src/styles.css      plain CSS
```

The API address is the `API_URL` line at the top of `src/App.jsx`. The ports
the backend accepts calls from are `FRONTEND_ORIGINS` in the settings.

## Endpoints

| Method | URL             | What it does                          |
| ------ | --------------- | ------------------------------------- |
| POST   | `/trainer/plan` | Returns BMI, diet plan, training plan |

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

`training_location` is `gym`, `home_with_dumbbells` or `home_body_weight`. It
decides which equipment the plan is allowed to use.

## Folders

```
app/
  api/             routes, controllers, middleware
  agent/           the graph, its nodes, the prompts, the tool loop
  domain/          pure rules: BMI, calories, unsafe exercises, equipment
  services/        plan_service runs the graph, plan_enrichment checks it
  clients/         USDA and ExerciseDB
  tools/           the 13 tools the model can call
  schemas/         the Pydantic models
  observability/   logging
  core/            settings and per-request state
frontend/          the React form
```

Two rules keep this honest:

- Files in `domain` import nothing but the schemas. No API, no model, no logging.
- Nothing in `domain` or `services` imports from `tools`.

## Data sources

USDA gives calories, macros and 14 micronutrients per food. It needs a free key
from https://fdc.nal.usda.gov/api-key-signup.html.

ExerciseDB gives 1500 exercises with instructions. It needs no key.

Both have the same trap: a bad request still answers `200 OK`.

- USDA answers every search, even nonsense. `zzzzqqq not a food` used to return
  Oats. Results that share no real word with the query are now dropped.
- ExerciseDB ignores a filter name it does not know and returns all 1500
  exercises. Filter names are checked against the API's own list first.

The model also invents food ids that look real. The tools only accept an id a
search actually showed.

## Logs

One file per run in `logs/`, named after the time the run started:

```
logs/2026-08-15_18-47-37-831.json
```

Each file is real JSON, so `json.load` reads it. It holds the request, a summary,
and every event of that run. The answer returns the id in `X-Request-Id`.

The summary says where the time and the money went:

```json
{
  "status_code": 200,
  "steps": { "design_diet_plan": 38209, "enrich_diet_plan": 17453 },
  "llm_calls": 2,
  "usda_calls": 15,
  "input_tokens": 9800,
  "output_tokens": 1450
}
```

The most useful event is `food_matched`. It writes the name we asked for next to
the name the API gave back:

```json
{ "asked": "Baked salmon", "matched": "Fish oil, salmon",
  "calories_before": 180.0, "calories_after": 1082.4 }
```

### Settings

| Setting             | What it does                                       |
| ------------------- | -------------------------------------------------- |
| `LOG_LEVEL`         | `DEBUG` also logs every USDA and ExerciseDB call   |
| `LOG_FOLDER`        | Where the run files go                             |
| `LOG_TO_CONSOLE`    | Turns the terminal lines off                       |
| `LOG_FULL_PAYLOADS` | Writes the full prompts and plans                  |
| `LOG_USER_DETAILS`  | Writes the profile, including medical conditions   |

The API key is never written to a log. `logs/` is in `.gitignore`.

