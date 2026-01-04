"""Workout parser response schemas.

This module defines the Pydantic models for structured output from the
workout parser agent (LLM).
"""

from typing import Optional

from pydantic import BaseModel, Field


class WorkoutParserResponse(BaseModel):
    """Structured output from the Parser Agent (LLM).

    This model represents the structured data extracted by the workout parser
    agent from natural language user input. All fields are optional to handle
    cases where information is not provided or cannot be extracted.

    Attributes
    ----------
    exercise : Optional[str]
        Name of the exercise (e.g., 'squats', 'bench press').
    sets : Optional[int]
        Number of sets performed.
    reps : Optional[int]
        Number of repetitions per set.
    weight : Optional[str]
        Weight used (e.g., '50 lbs', 'bodyweight', '20 kg').
    rest_time : Optional[int]
        Rest time between sets in seconds.
    comments : Optional[str]
        Any additional notes from the user.
    workout_id : Optional[str]
        Workout ID (UUID) if mentioned in user input for update/delete operations.

    Examples
    --------
    >>> response = WorkoutParserResponse(
    ...     exercise="squats",
    ...     sets=3,
    ...     reps=10,
    ...     weight="135 lbs"
    ... )
    """

    exercise: Optional[str] = Field(
        default=None, description="Name of the exercise (e.g., 'squats', 'bench press')"
    )
    sets: Optional[int] = Field(default=None, description="Number of sets performed")
    reps: Optional[int] = Field(
        default=None, description="Number of repetitions per set"
    )
    weight: Optional[str] = Field(
        default=None, description="Weight used (e.g., '50 lbs', 'bodyweight', '20 kg')"
    )
    rest_time: Optional[int] = Field(
        default=None, description="Rest time between sets in seconds"
    )
    comments: Optional[str] = Field(
        default=None, description="Any additional notes from the user"
    )
    workout_id: Optional[str] = Field(
        default=None,
        description="Workout ID (UUID) if mentioned in user input for update/delete operations",
    )
