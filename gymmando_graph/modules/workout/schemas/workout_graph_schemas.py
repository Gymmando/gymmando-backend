"""Workout graph state schemas.

This module defines the Pydantic models used for state management in the
workout graph workflow.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class WorkoutState(BaseModel):
    """State that flows through all nodes in the workout graph.

    This model represents the complete state of a workout operation as it
    flows through the LangGraph workflow. It contains user input, parsed
    workout data, validation results, and the final response.

    Attributes
    ----------
    user_input : str
        Original natural language input from the user.
    user_id : str
        Identifier for the user making the request.
    intent : Optional[str]
        Classified intent: "put" (create/update), "get" (read), or "delete".
    exercise : Optional[str]
        Name of the exercise extracted from user input.
    sets : Optional[int]
        Number of sets extracted from user input.
    reps : Optional[int]
        Number of repetitions per set extracted from user input.
    weight : Optional[str]
        Weight used (e.g., "135 lbs", "bodyweight", "20 kg").
    rest_time : Optional[int]
        Rest time between sets in seconds.
    comments : Optional[str]
        Additional notes or comments from the user.
    workout_id : Optional[str]
        UUID of the workout (as string) for update/delete operations.
    validation_status : Optional[str]
        Validation result: "complete" or "incomplete".
    missing_fields : List[str]
        List of required field names that are missing.
    response : str
        Final response message to return to the user.

    Examples
    --------
    >>> state = WorkoutState(
    ...     user_input="Squats 3x10 @ 135 lbs",
    ...     user_id="user123",
    ...     intent="put"
    ... )
    """

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
