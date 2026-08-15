from pydantic import BaseModel, Field


class Exercise(BaseModel):
    name: str = Field(description="Exercise name")
    sets: int = Field(description="Number of sets")
    reps: str = Field(description="Number of reps, for example 8-12")
    rest_seconds: int = Field(description="Rest between sets in seconds")


class WorkoutDay(BaseModel):
    day_number: int = Field(description="Day number in the week, starting from 1")
    focus: str = Field(description="Muscles or goal of this day, for example Upper Body")
    exercises: list[Exercise] = Field(description="Exercises of this day")


class TrainingPlan(BaseModel):
    """The training plan the model returns."""

    split_name: str = Field(description="Name of the split, for example Push Pull Legs")
    days_per_week: int = Field(description="How many training days in the week")
    workout_days: list[WorkoutDay] = Field(description="The training days")
    notes: list[str] = Field(description="Short advices, including the medical ones")
