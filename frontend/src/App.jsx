import { useState } from "react";

import PlanResult from "./PlanResult.jsx";

// Where the FastAPI backend listens. Start it with: uvicorn app.main:app --reload
const API_URL = "http://localhost:8000/trainer/plan";

// The form opens with these values, so the user only changes what is different.
// Every value is kept as text here, because that is what an <input> gives back.
const startingForm = {
  age: "28",
  gender: "male",
  weight_kg: "92",
  height_cm: "178",
  activity_level: "lightly_active",
  workout_days_per_week: "4",
  training_location: "gym",
  food_preferences: "chicken, rice",
  medical_conditions: "",
};

// The API wants a list, the user types one line: "chicken, rice" -> ["chicken", "rice"]
function textToList(text) {
  return text
    .split(",")
    .map((item) => item.trim())
    .filter((item) => item !== "");
}

export default function App() {
  // Four pieces of state: what the user typed, the answer, the error, and
  // whether we are still waiting for the server.
  const [form, setForm] = useState(startingForm);
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Every input calls this one function. It works because each input has a
  // name= that is exactly the same as its key in the form object above.
  function handleChange(event) {
    const { name, value } = event.target;
    setForm({ ...form, [name]: value });
  }

  async function handleSubmit(event) {
    event.preventDefault(); // without this the browser reloads the page

    setLoading(true);
    setError("");
    setPlan(null);

    // Turn the text of the form into the shape the API asks for:
    // real numbers for the numbers, real lists for the lists.
    const profile = {
      age: Number(form.age),
      gender: form.gender,
      weight_kg: Number(form.weight_kg),
      height_cm: Number(form.height_cm),
      activity_level: form.activity_level,
      workout_days_per_week: Number(form.workout_days_per_week),
      training_location: form.training_location,
      food_preferences: textToList(form.food_preferences),
      medical_conditions: textToList(form.medical_conditions),
    };

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profile),
      });

      if (!response.ok) {
        throw new Error("The server answered with status " + response.status);
      }

      const data = await response.json();
      setPlan(data);
    } catch (problem) {
      setError(problem.message);
    }

    // Runs after the try or the catch, so the button never stays stuck.
    setLoading(false);
  }

  return (
    <div className="page">
      <h1>Personal Trainer</h1>
      <p className="subtitle">
        Fill your data and get a diet plan and a training plan.
      </p>

      <form onSubmit={handleSubmit}>
        <label>
          Age
          <input
            type="number"
            name="age"
            value={form.age}
            onChange={handleChange}
            min="14"
            max="100"
            required
          />
        </label>

        <label>
          Gender
          <select name="gender" value={form.gender} onChange={handleChange}>
            <option value="male">Male</option>
            <option value="female">Female</option>
          </select>
        </label>

        <label>
          Weight (kg)
          <input
            type="number"
            name="weight_kg"
            value={form.weight_kg}
            onChange={handleChange}
            min="26"
            max="299"
            step="0.1"
            required
          />
        </label>

        <label>
          Height (cm)
          <input
            type="number"
            name="height_cm"
            value={form.height_cm}
            onChange={handleChange}
            min="101"
            max="249"
            step="0.1"
            required
          />
        </label>

        <label>
          Activity level
          <select
            name="activity_level"
            value={form.activity_level}
            onChange={handleChange}
          >
            <option value="sedentary">Sedentary</option>
            <option value="lightly_active">Lightly active</option>
            <option value="moderately_active">Moderately active</option>
            <option value="very_active">Very active</option>
            <option value="extremely_active">Extremely active</option>
          </select>
        </label>

        <label>
          Training days per week
          <input
            type="number"
            name="workout_days_per_week"
            value={form.workout_days_per_week}
            onChange={handleChange}
            min="1"
            max="7"
            required
          />
        </label>

        <label>
          Where do you train
          <select
            name="training_location"
            value={form.training_location}
            onChange={handleChange}
          >
            <option value="gym">Gym</option>
            <option value="home_with_dumbbells">Home with dumbbells</option>
            <option value="home_body_weight">Home, body weight only</option>
          </select>
        </label>

        <label className="wide">
          Food preferences
          <input
            type="text"
            name="food_preferences"
            value={form.food_preferences}
            onChange={handleChange}
            placeholder="chicken, rice, no seafood"
          />
          <span className="hint">Separate them with a comma.</span>
        </label>

        <label className="wide">
          Medical conditions
          <input
            type="text"
            name="medical_conditions"
            value={form.medical_conditions}
            onChange={handleChange}
            placeholder="knee pain"
          />
          <span className="hint">Leave it empty if you have none.</span>
        </label>

        <button type="submit" disabled={loading}>
          {loading ? "Building your plan..." : "Get my plan"}
        </button>
      </form>

      {/* Each of these only shows up when it has something to say. */}
      {loading && (
        <p className="note">
          The agent is looking up real foods and exercises. This takes about a
          minute.
        </p>
      )}

      {error && <p className="error">{error}</p>}

      {plan && <PlanResult plan={plan} />}
    </div>
  );
}
