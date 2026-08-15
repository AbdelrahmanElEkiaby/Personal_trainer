from enum import Enum

from pydantic import BaseModel, Field


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class TrainingLocation(str, Enum):
    """Where the person trains. We use it to know which equipment they can use."""

    HOME_BODY_WEIGHT = "home_body_weight"
    HOME_WITH_DUMBBELLS = "home_with_dumbbells"
    GYM = "gym"


class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"


class UserProfile(BaseModel):
    """The information we ask the user for before building any plan."""

    age: int = Field(ge=14, le=100, description="Age in years")
    gender: Gender = Field(description="Used to calculate the calorie needs")
    weight_kg: float = Field(gt=25, lt=300, description="Weight in kilograms")
    height_cm: float = Field(gt=100, lt=250, description="Height in centimeters")
    activity_level: ActivityLevel = Field(description="How active the user is during a normal day")
    food_preferences: list[str] = Field(
        default_factory=list,
        description="Foods the user likes, or a diet style such as vegetarian",
    )
    workout_days_per_week: int = Field(ge=1, le=7, description="How many days the user can train")
    training_location: TrainingLocation = Field(
        default=TrainingLocation.GYM,
        description="Where the user trains, it decides which equipment we can use",
    )
    medical_conditions: list[str] = Field(
        default_factory=list,
        description="Health problems to consider in the diet or in the training",
    )
