from pydantic import BaseModel, Field


class PlannedExercise(BaseModel):
    """One exercise inside a training day.

    It is called Planned to keep it different from ExerciseInfo, which is the
    exercise as ExerciseDB describes it.
    """

    # Empty for now. When the graph uses the ExerciseDB tools, we fill this id and
    # then we can also show the instructions and the animation of the movement.
    exercise_id: str = Field(default="", description="The ExerciseDB id, empty if we do not have it")
    name: str = Field(description="Name of the exercise")
    target_muscles: list[str] = Field(description="The main muscles this exercise trains")
    equipments: list[str] = Field(description="The equipment needed for this exercise")
    sets: int = Field(description="Number of sets")
    reps: str = Field(description="Number of reps, for example 8-12")
    rest_seconds: int = Field(description="Rest between sets in seconds")


class AvoidedExercise(BaseModel):
    """One exercise we did not use because of a medical condition."""

    exercise: str = Field(description="The exercise we did not use")
    reason: str = Field(description="The medical condition that makes it dangerous")
    replaced_with: str = Field(description="The safe exercise we used instead")


class WorkoutDay(BaseModel):
    """One training day."""

    day_number: int = Field(description="Day number in the week, starting from 1")
    focus: str = Field(description="Muscles or goal of this day, for example Upper Body")
    exercises: list[PlannedExercise] = Field(description="Exercises of this day")


class TrainingPlan(BaseModel):
    """The training plan the model returns."""

    split_name: str = Field(description="Name of the split, for example Push Pull Legs")
    days_per_week: int = Field(description="How many training days in the week")
    workout_days: list[WorkoutDay] = Field(description="Only the days that have a workout")
    avoided_exercises: list[AvoidedExercise] = Field(
        description="The exercises we skipped because of a medical condition"
    )
    safety_notes: list[str] = Field(description="Warnings the person must read before training")
    notes: list[str] = Field(description="General advices, for example how to add weight")
