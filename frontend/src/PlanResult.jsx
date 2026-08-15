// This file only shows the answer. It never calls the API and it never
// changes anything, it just reads the plan that App.jsx gives it.

export default function PlanResult({ plan }) {
  // The API answers with these three parts.
  const bmi = plan.bmi_result;
  const diet = plan.diet_plan;
  const training = plan.training_plan;

  return (
    <div className="result">
      <h2>Your numbers</h2>
      <div className="cards">
        <Card label="BMI" value={bmi.bmi} />
        <Card label="Category" value={bmi.category} />
        <Card label="Rest calories" value={bmi.bmr_calories} />
        <Card label="Maintenance" value={bmi.maintenance_calories} />
      </div>

      <h2>Diet plan</h2>
      <div className="cards">
        <Card label="Calories a day" value={diet.daily_calories} />
        <Card label="Protein" value={diet.protein_grams + " g"} />
        <Card label="Carbs" value={diet.carbs_grams + " g"} />
        <Card label="Fat" value={diet.fat_grams + " g"} />
      </div>

      {/* .map() draws one block for every meal in the list. React asks for a
          key on each one so it can tell them apart. The position in the list is
          a fine key here, because we draw the answer once and never reorder it. */}
      {diet.meals.map((meal, index) => (
        <div className="box" key={index}>
          <h3>
            {meal.name} <small>{meal.total_calories} kcal</small>
          </h3>
          <table>
            <thead>
              <tr>
                <th>Food</th>
                <th>Portion</th>
                <th>Calories</th>
                <th>Protein</th>
                <th>Carbs</th>
                <th>Fat</th>
              </tr>
            </thead>
            <tbody>
              {meal.foods.map((food, index) => (
                <tr key={index}>
                  <td>{food.food_name}</td>
                  <td>{food.portion}</td>
                  <td>{food.calories}</td>
                  <td>{food.protein_grams} g</td>
                  <td>{food.carbs_grams} g</td>
                  <td>{food.fat_grams} g</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}

      <NoteList title="Diet notes" notes={diet.notes} />

      <h2>Training plan</h2>
      <p className="subtitle">
        {training.split_name} — {training.days_per_week} days a week
      </p>

      {training.workout_days.map((day, index) => (
        <div className="box" key={index}>
          <h3>
            Day {day.day_number} <small>{day.focus}</small>
          </h3>
          <table>
            <thead>
              <tr>
                <th>Exercise</th>
                <th>Sets</th>
                <th>Reps</th>
                <th>Rest</th>
                <th>Muscles</th>
                <th>Equipment</th>
              </tr>
            </thead>
            <tbody>
              {day.exercises.map((exercise, index) => (
                <tr key={index}>
                  <td>{exercise.name}</td>
                  <td>{exercise.sets}</td>
                  <td>{exercise.reps}</td>
                  <td>{exercise.rest_seconds} s</td>
                  <td>{exercise.target_muscles.join(", ")}</td>
                  <td>{exercise.equipments.join(", ")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}

      {/* This one is often empty, so we only draw it when it has something. */}
      {training.avoided_exercises.length > 0 && (
        <div className="box">
          <h3>Exercises we skipped</h3>
          <ul>
            {training.avoided_exercises.map((item, index) => (
              <li key={index}>
                <strong>{item.exercise}</strong> — {item.reason}. Replaced with{" "}
                {item.replaced_with}.
              </li>
            ))}
          </ul>
        </div>
      )}

      <NoteList title="Safety notes" notes={training.safety_notes} />
      <NoteList title="Training notes" notes={training.notes} />
    </div>
  );
}

// A tiny component for one number. We use it 8 times above instead of
// writing the same three lines of HTML 8 times.
function Card({ label, value }) {
  return (
    <div className="card">
      <span className="card-label">{label}</span>
      <span className="card-value">{value}</span>
    </div>
  );
}

// The same idea for the four lists of short advices.
function NoteList({ title, notes }) {
  if (notes.length === 0) {
    return null; // returning null means "draw nothing"
  }

  return (
    <div className="box">
      <h3>{title}</h3>
      <ul>
        {notes.map((note, index) => (
          <li key={index}>{note}</li>
        ))}
      </ul>
    </div>
  );
}
