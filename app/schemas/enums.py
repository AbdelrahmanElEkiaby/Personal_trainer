"""Every fixed list of choices the app uses, all in one place.

They all inherit from str so FastAPI shows them in the docs and reads them from
JSON as normal text.
"""

from enum import Enum


class Gender(str, Enum):
    """Needed because the calorie formula is not the same for everybody."""

    MALE = "male"
    FEMALE = "female"


class ActivityLevel(str, Enum):
    """How active the person is during a normal day, outside of training."""

    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"
    EXTREMELY_ACTIVE = "extremely_active"


class TrainingLocation(str, Enum):
    """Where the person trains. We use it to know which equipment they can use."""

    HOME_BODY_WEIGHT = "home_body_weight"
    HOME_WITH_DUMBBELLS = "home_with_dumbbells"
    GYM = "gym"
