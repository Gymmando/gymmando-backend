"""Workout validator node module.

This module provides validation logic for workout data to ensure all required
fields are present before saving to the database.
"""

from gymmando_graph.modules.workout.schemas import WorkoutState


class WorkoutValidator:
    """Validates workout data completeness.

    Checks that all required workout fields are present and non-empty.
    Updates the state with validation status and list of missing fields.

    Attributes
    ----------
    REQUIRED_FIELDS : list[str]
        List of field names that must be present for a valid workout:
        ["exercise", "sets", "reps", "weight"].

    Examples
    --------
    >>> validator = WorkoutValidator()
    >>> state = WorkoutState(exercise="squats", sets=3, reps=10, weight="135 lbs")
    >>> validated_state = validator.validate(state)
    >>> print(validated_state.validation_status)  # "complete"
    """

    REQUIRED_FIELDS = ["exercise", "sets", "reps", "weight"]

    def __init__(self):
        """Initialize the WorkoutValidator.

        Sets up the validator with the list of required fields.
        """

    def validate(self, state: WorkoutState) -> WorkoutState:
        """Check if all required workout fields are present.

        Validates that exercise, sets, reps, and weight are all present
        and non-empty. Updates the state with validation status and
        missing fields list.

        Parameters
        ----------
        state : WorkoutState
            Current workout state to validate.

        Returns
        -------
        WorkoutState
            Updated state with:
            - validation_status: "complete" if all fields present, "incomplete" otherwise
            - missing_fields: List of field names that are missing or empty.

        Notes
        -----
        Fields are considered missing if they are None or empty strings.
        The state object is modified in-place and returned.
        """
        missing_fields = []

        for field in self.REQUIRED_FIELDS:
            value = getattr(state, field, None)
            if value is None or value == "":
                missing_fields.append(field)

        # Update state
        state.validation_status = "complete" if not missing_fields else "incomplete"
        state.missing_fields = missing_fields

        return state
