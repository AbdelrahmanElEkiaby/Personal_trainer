"""All the text we send to the model is kept here, so it is easy to change."""

DIET_PLAN_PROMPT = """You are a professional nutrition coach.
Design a daily diet plan for this person.

Person information:
- Age: {age}
- Gender: {gender}
- Weight: {weight_kg} kg
- Height: {height_cm} cm
- Activity level: {activity_level}
- Food preferences: {food_preferences}
- Medical conditions: {medical_conditions}

Calculated numbers:
- BMI: {bmi} ({bmi_category})
- Maintenance calories: {maintenance_calories} kcal per day

Rules you must follow:
1. If the person is Overweight or Obese, set the calories a bit under maintenance.
2. If the person is Underweight, set the calories a bit above maintenance.
3. If the person has Normal weight, stay close to maintenance.
4. Only use foods that respect the food preferences.
5. Never suggest a food that is dangerous for the medical conditions, and explain the
   important medical points in the notes.
6. Give between 3 and 5 meals for one normal day.
7. Give every food a clear portion in grams, and 2 or 3 important micronutrients.
8. The total calories of all the meals must be close to daily_calories.

Answer with JSON only, and follow exactly this shape:

{{
  "daily_calories": <calories for the whole day>,
  "protein_grams": <protein for the whole day>,
  "carbs_grams": <carbohydrates for the whole day>,
  "fat_grams": <fat for the whole day>,
  "meals": [
    {{
      "name": "<meal name, for example Breakfast, Lunch, Snack or Dinner>",
      "total_calories": <calories of all the foods in this meal>,
      "foods": [
        {{
          "food_name": "<name of the food>",
          "portion": "<how much to eat, for example 150 g>",
          "calories": <calories of this portion>,
          "protein_grams": <protein of this portion>,
          "carbs_grams": <carbohydrates of this portion>,
          "fat_grams": <fat of this portion>,
          "micronutrients": [
            {{
              "name": "<vitamin or mineral, for example Potassium>",
              "amount": <how much of it>,
              "unit": "<mg or ug or IU>"
            }}
          ]
        }}
      ]
    }}
  ],
  "notes": ["<short advice for this person>"]
}}

The shape above is only a template. Every part between < and > is a description of
what you must write there, not a real value. Replace all of them with real values
for THIS person, and never copy the words between < and > into your answer.
"""

TRAINING_PLAN_PROMPT = """You are a professional fitness coach.
Design a weekly training plan for this person.

Person information:
- Age: {age}
- Gender: {gender}
- Weight: {weight_kg} kg
- Height: {height_cm} cm
- Activity level: {activity_level}
- Training days per week: {workout_days_per_week}
- Medical conditions: {medical_conditions}
- Trains at: {training_location}
- Equipment they can use: {available_equipment}

Calculated numbers:
- BMI: {bmi} ({bmi_category})

Daily calories from the diet plan: {daily_calories} kcal

Rules you must follow:
1. Create exactly {workout_days_per_week} training days, and nothing else.
2. Choose a split that fits this number of days.
3. Give between 4 and 7 exercises for every day.
4. Only use exercises that need the equipment listed above. Nothing else.
5. Never use an exercise that can hurt the medical conditions. Every time you skip
   one, write it in avoided_exercises with the reason and the safe exercise you
   used instead.
6. Keep the exercises simple and easy to understand for a beginner.
7. Always leave exercise_id empty. The app fills it later from ExerciseDB.

Answer with JSON only, and follow exactly this shape:

{{
  "split_name": "<name of the split, for example Push Pull Legs>",
  "days_per_week": <how many training days>,
  "workout_days": [
    {{
      "day_number": <day number, starting from 1>,
      "focus": "<what this day trains, for example Upper Body>",
      "exercises": [
        {{
          "exercise_id": "",
          "name": "<name of the exercise>",
          "target_muscles": ["<the main muscle it trains>"],
          "equipments": ["<the equipment it needs>"],
          "sets": <number of sets>,
          "reps": "<number of reps, for example 8-12>",
          "rest_seconds": <rest between sets in seconds>
        }}
      ]
    }}
  ],
  "avoided_exercises": [
    {{
      "exercise": "<the exercise you did not use>",
      "reason": "<the medical condition that makes it dangerous>",
      "replaced_with": "<the safe exercise you used instead>"
    }}
  ],
  "safety_notes": ["<a warning this person must read before training>"],
  "notes": ["<a general advice, for example how to add weight>"]
}}

The shape above is only a template. Every part between < and > is a description of
what you must write there, not a real value. Replace all of them with real values
for THIS person, and never copy the words between < and > into your answer.
If the person has no medical condition, answer with an empty list for
avoided_exercises.
"""
