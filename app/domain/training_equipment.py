"""Turns the training location into the equipment names ExerciseDB understands.

The names here must be written exactly like ExerciseDB writes them, if not the
API ignores the filter and sends back every exercise. The full list of names
comes from app/clients/exercisedb_client.py -> get_equipments().
"""

from app.schemas.enums import TrainingLocation

EQUIPMENT_BY_LOCATION = {
    TrainingLocation.HOME_BODY_WEIGHT: [
        "body weight",
    ],
    TrainingLocation.HOME_WITH_DUMBBELLS: [
        "body weight",
        "dumbbell",
        "resistance band",
    ],
    TrainingLocation.GYM: [
        "body weight",
        "barbell",
        "dumbbell",
        "cable",
        "leverage machine",
        "smith machine",
        "kettlebell",
        "ez barbell",
        "olympic barbell",
        "resistance band",
        "stability ball",
        "medicine ball",
    ],
}


def get_equipment_for_location(training_location: TrainingLocation) -> list[str]:
    """Give the equipment the person can really use where they train."""
    return EQUIPMENT_BY_LOCATION[training_location]
