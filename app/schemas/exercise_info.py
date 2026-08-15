from pydantic import BaseModel, Field


class ExerciseInfo(BaseModel):
    """One exercise as ExerciseDB describes it.

    ExerciseDB answers with lists, because one exercise can train more than one
    body part and can need more than one equipment.
    """

    exercise_id: str = Field(description="The id ExerciseDB uses for this exercise")
    name: str = Field(description="Name of the exercise")
    body_parts: list[str] = Field(
        default_factory=list,
        description="The big body parts, for example chest or upper legs",
    )
    target_muscles: list[str] = Field(
        default_factory=list,
        description="The main muscles the exercise trains",
    )
    equipments: list[str] = Field(
        default_factory=list,
        description="The equipment needed, for example barbell or body weight",
    )
    secondary_muscles: list[str] = Field(
        default_factory=list,
        description="The other muscles the exercise also trains",
    )
    instructions: list[str] = Field(
        default_factory=list,
        description="The steps that explain how to do the exercise",
    )
    gif_url: str = Field(default="", description="A small animation that shows the movement")
