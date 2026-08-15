"""All the health math lives here so the rest of the app stays simple."""

from app.schemas.bmi_result import BmiResult
from app.schemas.enums import ActivityLevel, Gender
from app.schemas.user_profile import UserProfile

# How much we multiply the resting calories by, based on the activity level.
ACTIVITY_MULTIPLIERS = {
    ActivityLevel.SEDENTARY: 1.2,
    ActivityLevel.LIGHTLY_ACTIVE: 1.375,
    ActivityLevel.MODERATELY_ACTIVE: 1.55,
    ActivityLevel.VERY_ACTIVE: 1.725,
    ActivityLevel.EXTREMELY_ACTIVE: 1.9,
}


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """BMI = weight in kg divided by the height in meters squared."""
    height_m = height_cm / 100
    bmi = weight_kg / (height_m**2)
    return round(bmi, 1)


def get_bmi_category(bmi: float) -> str:
    """Turn the BMI number into the category the user understands."""
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal weight"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def calculate_bmr(user_profile: UserProfile) -> float:
    """Calories burned at rest, using the Mifflin-St Jeor formula."""
    base = (10 * user_profile.weight_kg) + (6.25 * user_profile.height_cm) - (5 * user_profile.age)
    if user_profile.gender == Gender.MALE:
        return base + 5
    return base - 161


def calculate_maintenance_calories(user_profile: UserProfile) -> float:
    """Resting calories multiplied by how active the user is."""
    bmr = calculate_bmr(user_profile)
    multiplier = ACTIVITY_MULTIPLIERS[user_profile.activity_level]
    return bmr * multiplier


def build_bmi_result(user_profile: UserProfile) -> BmiResult:
    """Collect every calculated number in one object."""
    bmi = calculate_bmi(user_profile.weight_kg, user_profile.height_cm)
    return BmiResult(
        bmi=bmi,
        category=get_bmi_category(bmi),
        bmr_calories=round(calculate_bmr(user_profile)),
        maintenance_calories=round(calculate_maintenance_calories(user_profile)),
    )
