"""Database models for Supabase tables.

This module defines Pydantic models that represent the database schema for
type-safe database operations. Models include both read (full) and create
(partial) variants.
"""

import uuid
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class WorkoutDBModel(BaseModel):
    """Database model for the workouts table.

    This model represents a complete workout record as stored in Supabase.
    All fields match the database schema exactly, including auto-generated
    fields like id and created_at.

    Attributes
    ----------
    id : UUID
        Primary key, auto-generated UUID.
    user_id : str
        User identifier (Firebase UID).
    exercise : str
        Name of the exercise.
    sets : int
        Number of sets performed.
    reps : int
        Number of repetitions per set.
    weight : str
        Weight used (e.g., '135 lbs', 'bodyweight').
    rest_time : Optional[int]
        Rest time between sets in seconds.
    comments : Optional[str]
        Additional notes or comments.
    created_at : Optional[datetime]
        Timestamp when record was created (auto-generated).

    Examples
    --------
    >>> workout = WorkoutDBModel(
    ...     id=uuid.uuid4(),
    ...     user_id="user123",
    ...     exercise="squats",
    ...     sets=3,
    ...     reps=10,
    ...     weight="135 lbs"
    ... )
    """

    id: UUID = Field(default_factory=uuid.uuid4, description="Primary key")
    user_id: str = Field(..., description="User identifier (Firebase UID)")
    exercise: str = Field(..., description="Name of the exercise")
    sets: int = Field(..., description="Number of sets performed")
    reps: int = Field(..., description="Number of repetitions per set")
    weight: str = Field(..., description="Weight used (e.g., '135 lbs', 'bodyweight')")
    rest_time: Optional[int] = Field(
        default=None, description="Rest time between sets in seconds"
    )
    comments: Optional[str] = Field(
        default=None, description="Additional notes or comments"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow, description="Timestamp when record was created"
    )

    class Config:
        """Pydantic configuration for the model.

        Configures JSON encoding for UUID and datetime fields, and enables
        ORM mode for compatibility with database ORMs.
        """

        from_attributes = True
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }


class WorkoutCreateModel(BaseModel):
    """Model for creating a new workout record.

    Excludes auto-generated fields like id and created_at. Used when
    inserting new workouts into the database. All fields except rest_time
    and comments are required.

    Attributes
    ----------
    user_id : str
        User identifier (Firebase UID).
    exercise : str
        Name of the exercise.
    sets : int
        Number of sets performed.
    reps : int
        Number of repetitions per set.
    weight : str
        Weight used (e.g., '135 lbs', 'bodyweight').
    rest_time : Optional[int], optional
        Rest time between sets in seconds.
    comments : Optional[str], optional
        Additional notes or comments.

    Examples
    --------
    >>> create_model = WorkoutCreateModel(
    ...     user_id="user123",
    ...     exercise="squats",
    ...     sets=3,
    ...     reps=10,
    ...     weight="135 lbs"
    ... )
    >>> db_dict = create_model.to_db_dict()
    """

    user_id: str
    exercise: str
    sets: int
    reps: int
    weight: str
    rest_time: Optional[int] = None
    comments: Optional[str] = None

    def to_db_dict(self) -> dict[str, Any]:
        """Convert to dictionary suitable for database insertion.

        Excludes None values to avoid inserting null fields unnecessarily.

        Returns
        -------
        dict[str, Any]
            Dictionary representation of the model with None values excluded,
            ready for Supabase insertion.
        """
        return dict(self.model_dump(exclude_none=True))
