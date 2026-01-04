from typing import List, Optional

from pydantic import BaseModel, Field


class WorkoutState(BaseModel):
    """State that flows through all nodes."""

    # User input
    user_input: str
    user_id: str

    # Intent classification
    intent: Optional[str] = None  # "put" or "get"

    # Workout data (extracted by parser)
    exercise: Optional[str] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[str] = None
    rest_time: Optional[int] = None
    comments: Optional[str] = None

    # Workout identifier (for update/delete operations)
    workout_id: Optional[str] = None  # UUID as string, extracted from user input

    # Validation results
    validation_status: Optional[str] = None  # "complete" or "incomplete"
    missing_fields: List[str] = Field(default_factory=list)

    # Response
    response: str = ""
