"""Workout CRUD operations module.

This module provides database operations for the workouts table including
create, read (query), update, and delete operations using Supabase.
"""

from typing import List, Optional
from uuid import UUID

from gymmando_graph.database import get_supabase_client
from gymmando_graph.database.models import WorkoutCreateModel, WorkoutDBModel
from gymmando_graph.modules.workout.schemas import WorkoutState
from gymmando_graph.utils import Logger

logger = Logger().get_logger()


class WorkoutCRUD:
    """CRUD operations for workout table.

    Provides methods for creating, querying, updating, and deleting workout
    records in the Supabase database. All operations are scoped to user_id
    for security.

    Attributes
    ----------
    table_name : str
        Name of the database table ("workouts").

    Examples
    --------
    >>> crud = WorkoutCRUD()
    >>> workout = crud.create(state)
    >>> workouts = crud.query(user_id="user123", exercise="squats", limit=5)
    >>> updated = crud.update(workout_id, user_id, {"sets": 4})
    >>> success = crud.delete(workout_id, user_id)
    """

    def __init__(self):
        """Initialize the workout CRUD service.

        Sets up the table name for workout operations. The Supabase client
        is loaded lazily on first use.
        """
        self.table_name = "workouts"

    def _get_client(self):
        """Get Supabase client instance (lazy loading).

        Returns
        -------
        Client
            Initialized Supabase client for database operations.
        """
        return get_supabase_client()

    def create(self, state: WorkoutState) -> Optional[WorkoutDBModel]:
        """Create a new workout record in the database.

        Validates that all required fields (exercise, sets, reps, weight) are
        present, then inserts a new workout record into the database.

        Parameters
        ----------
        state : WorkoutState
            State containing workout data to create (exercise, sets, reps,
            weight, rest_time, comments, user_id).

        Returns
        -------
        Optional[WorkoutDBModel]
            Created workout model if successful, None if database insert
            returned no data.

        Raises
        ------
        ValueError
            If required fields (exercise, sets, reps, weight) are missing.
        Exception
            Re-raises any database errors that occur during insertion.
        """
        # Validate that required fields are present
        if not state.exercise or not state.sets or not state.reps or not state.weight:
            error_msg = "Cannot create workout: missing required fields"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Create database model from state
        workout_create = WorkoutCreateModel(
            user_id=state.user_id,
            exercise=state.exercise,
            sets=state.sets,
            reps=state.reps,
            weight=state.weight,
            rest_time=state.rest_time,
            comments=state.comments,
        )

        try:
            logger.info(
                f"💾 Creating workout: {workout_create.exercise} - "
                f"{workout_create.sets}x{workout_create.reps} @ {workout_create.weight} "
                f"for user_id: {workout_create.user_id}"
            )

            client = self._get_client()
            response = (
                client.table(self.table_name)
                .insert(workout_create.to_db_dict())
                .execute()
            )

            if response.data and len(response.data) > 0:
                saved_workout = WorkoutDBModel(**response.data[0])
                logger.info(f"Workout created successfully with ID: {saved_workout.id}")
                return saved_workout
            else:
                logger.error("Database insert returned no data")
                return None

        except Exception as e:
            logger.error(f"Failed to create workout: {e}", exc_info=True)
            raise

    def query(
        self,
        user_id: str,
        exercise: Optional[str] = None,
        exercise_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = 10,
        order_by: Optional[str] = "created_at",
        order_direction: Optional[str] = "desc",
    ) -> List[WorkoutDBModel]:
        """Query workouts from the database based on filters.

        Reads workout records matching the specified filters. All queries
        are scoped to the provided user_id for security.

        Parameters
        ----------
        user_id : str
            The user ID to filter workouts by (required).
        exercise : Optional[str], optional
            Filter by specific exercise name using case-insensitive partial
            matching (e.g., "squats", "bench press").
        exercise_type : Optional[str], optional
            Filter by exercise type/category (e.g., "legs", "chest", "arms").
            Currently not implemented in database schema.
        start_date : Optional[str], optional
            Start date for date range filter in YYYY-MM-DD format.
        end_date : Optional[str], optional
            End date for date range filter in YYYY-MM-DD format.
        limit : Optional[int], optional
            Maximum number of workouts to return (default: 10).
        order_by : Optional[str], optional
            Field to order by (default: "created_at").
        order_direction : Optional[str], optional
            Order direction - "asc" or "desc" (default: "desc").

        Returns
        -------
        List[WorkoutDBModel]
            List of workout models matching the query criteria. Returns empty
            list if no workouts found or on error.

        Notes
        -----
        Errors are caught and logged, but an empty list is returned rather
        than raising exceptions to allow the workflow to continue.
        """
        try:
            logger.info(
                f"🔍 Reading workouts with params: user_id={user_id}, "
                f"exercise={exercise}, limit={limit}"
            )

            client = self._get_client()
            query = client.table(self.table_name).select("*").eq("user_id", user_id)

            # Apply filters
            if exercise:
                query = query.ilike("exercise", f"%{exercise}%")
                logger.info(f"Applied exercise filter: {exercise}")

            # TODO: Add exercise_type filtering when we have that field in the schema

            if start_date:
                query = query.gte("created_at", start_date)

            if end_date:
                query = query.lte("created_at", end_date)

            # Apply ordering
            desc_order = (order_direction or "desc").lower() == "desc"
            query = query.order(order_by or "created_at", desc=desc_order)

            # Apply limit
            if limit:
                query = query.limit(limit)

            # Execute query
            response = query.execute()
            logger.info(
                f"Query returned {len(response.data) if response.data else 0} workouts"
            )

            if response.data:
                return [WorkoutDBModel(**item) for item in response.data]

            return []

        except Exception as e:
            logger.error(f"Failed to read workouts: {e}", exc_info=True)
            return []

    def update(
        self, workout_id: UUID, user_id: str, data: dict
    ) -> Optional[WorkoutDBModel]:
        """Update an existing workout record in the database.

        Updates specified fields of a workout identified by workout_id.
        Only updates workouts belonging to the specified user_id for security.

        Parameters
        ----------
        workout_id : UUID
            UUID of the workout to update.
        user_id : str
            User ID for security filtering (ensures users can only update
            their own workouts).
        data : dict
            Dictionary containing the fields to update. Keys should match
            database column names (e.g., {"sets": 5, "reps": 10, "weight": "225 lbs"}).

        Returns
        -------
        Optional[WorkoutDBModel]
            Updated workout model if successful, None if workout not found
            or user doesn't have permission.

        Notes
        -----
        The update operation uses both workout_id and user_id in the WHERE
        clause to ensure users can only update their own workouts.
        """
        try:
            logger.info(
                f"✏️ Updating workout {workout_id} for user {user_id} with data: {data}"
            )

            client = self._get_client()
            response = (
                client.table(self.table_name)
                .update(data)
                .eq("id", str(workout_id))
                .eq("user_id", user_id)
                .execute()
            )

            if response.data and len(response.data) > 0:
                updated_workout = WorkoutDBModel(**response.data[0])
                logger.info(f"Workout {workout_id} updated successfully")
                return updated_workout
            else:
                logger.warning(
                    f"No workout found with ID {workout_id} for user {user_id}"
                )
                return None

        except Exception as e:
            logger.error(f"Failed to update workout {workout_id}: {e}", exc_info=True)
            return None

    def delete(self, workout_id: UUID, user_id: str) -> bool:
        """Delete a workout record from the database.

        Removes a workout identified by workout_id. Only deletes workouts
        belonging to the specified user_id for security.

        Parameters
        ----------
        workout_id : UUID
            UUID of the workout to delete.
        user_id : str
            User ID for security filtering (ensures users can only delete
            their own workouts).

        Returns
        -------
        bool
            True if deletion was successful, False if an error occurred.

        Notes
        -----
        The delete operation uses both workout_id and user_id in the WHERE
        clause to ensure users can only delete their own workouts. Supabase
        returns an empty array on successful deletion.
        """
        try:
            logger.info(f"🗑️ Deleting workout {workout_id} for user {user_id}")

            client = self._get_client()
            response = (
                client.table(self.table_name)
                .delete()
                .eq("id", str(workout_id))
                .eq("user_id", user_id)
                .execute()
            )

            # Supabase delete returns empty array on success
            # If no exception was thrown, deletion succeeded
            logger.info(f"Workout {workout_id} deleted successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to delete workout {workout_id}: {e}", exc_info=True)
            return False
