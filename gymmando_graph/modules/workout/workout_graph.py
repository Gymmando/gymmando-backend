from typing import Any, Literal, cast

from langgraph.graph import END, START, StateGraph

from gymmando_graph.modules.workout.agents import WorkoutCreator, WorkoutReader
from gymmando_graph.modules.workout.crud import WorkoutCRUD
from gymmando_graph.modules.workout.nodes.workout_validator import WorkoutValidator
from gymmando_graph.modules.workout.schemas import WorkoutState
from gymmando_graph.utils import Logger

logger = Logger().get_logger()


class WorkoutGraph:
    def __init__(self):
        # initialize the workout creator
        self.workout_creator = WorkoutCreator()
        # initialize the validator
        self.validator = WorkoutValidator()
        # initialize the database service
        self.database = WorkoutCRUD()
        # initialize the reader agent
        self.reader = WorkoutReader()

        # create the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(WorkoutState)

        # add nodes
        workflow.add_node("workout_creator", self._workout_creator_node)
        workflow.add_node("workout_validator", self._workout_validator_node)
        workflow.add_node("workout_saver", self._workout_saver_node)
        workflow.add_node("workout_reader", self._workout_reader_node)

        # add edges
        workflow.add_edge(START, "workout_creator")
        # Route based on intent: get -> reader, put -> validator
        workflow.add_conditional_edges(
            "workout_creator",
            self._route_by_intent,
            {
                "reader": "workout_reader",
                "validator": "workout_validator",
            },
        )
        workflow.add_edge("workout_reader", END)
        workflow.add_conditional_edges(
            "workout_validator",
            self._should_save_to_database,
            {
                "database": "workout_saver",
                "end": END,
            },
        )
        workflow.add_edge("workout_saver", END)

        return workflow.compile()

    def _route_by_intent(self, state: WorkoutState) -> Literal["reader", "validator"]:
        """
        Route based on intent after parsing.

        Routes to reader if intent is "get" (read operation).
        Routes to validator if intent is "put" (create operation).
        """
        if state.intent == "get":
            return "reader"
        return "validator"

    def _should_save_to_database(
        self, state: WorkoutState
    ) -> Literal["database", "end"]:
        """
        Determine if workout should be saved to database.

        Routes to database if:
        - intent is "put" (save operation)
        - validation_status is "complete" (all required fields present)

        Otherwise routes to end.
        """
        if state.intent == "put" and state.validation_status == "complete":
            return "database"
        return "end"

    def _workout_creator_node(self, state: WorkoutState) -> WorkoutState:
        """Create workout object from user input."""
        # Process the user input through the creator
        parsed_result = self.workout_creator.process(state.user_input)

        # Update state with parsed workout data
        state.exercise = parsed_result.exercise
        state.sets = parsed_result.sets
        state.reps = parsed_result.reps
        state.weight = parsed_result.weight
        state.rest_time = parsed_result.rest_time
        state.comments = parsed_result.comments
        state.workout_id = parsed_result.workout_id

        return state

    def _workout_reader_node(self, state: WorkoutState) -> WorkoutState:
        """Read workout data based on user query."""
        try:
            logger.info(f"Retrieving workouts for user: {state.user_id}")
            result = self.reader.retrieve(state.user_input, state.user_id)
            state.response = result
            logger.info("Workout retrieval completed successfully")
        except Exception as e:
            logger.error(f"Error retrieving workouts: {e}", exc_info=True)
            state.response = "Sorry, I encountered an error retrieving your workouts. Please try again."
        return state

    def _workout_validator_node(self, state: WorkoutState) -> WorkoutState:
        """Validate that all required workout fields are present."""
        return cast(WorkoutState, self.validator.validate(state))

    def _workout_saver_node(self, state: WorkoutState) -> WorkoutState:
        """Save workout to database. Called only when validation is complete and intent is 'put'."""
        try:
            logger.info("Attempting to save workout to database...")
            saved_workout = self.database.create(state)

            if saved_workout:
                logger.info(f"Workout saved successfully with ID: {saved_workout.id}")
                state.response = f"Workout saved! {state.exercise}: {state.sets}x{state.reps} @ {state.weight}"
            else:
                logger.error("Failed to save workout - database returned None")
                state.response = "Failed to save workout. Please try again."

        except ValueError as e:
            logger.error(f"Validation error while saving workout: {e}")
            state.response = f"Cannot save workout: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error while saving workout: {e}", exc_info=True)
            state.response = (
                "An error occurred while saving your workout. Please try again."
            )

        return state

    def _workout_updator_node(self, state: WorkoutState) -> WorkoutState:
        """Update workout in database. Requires workout_id and fields to update."""
        try:
            from uuid import UUID

            if not state.workout_id:
                state.response = "Cannot update workout: workout ID is required. Please specify which workout to update."
                logger.error("Workout ID missing for update operation")
                return state

            # Build update data from state fields that are present
            update_data: dict[str, Any] = {}
            if state.exercise is not None:
                update_data["exercise"] = state.exercise
            if state.sets is not None:
                update_data["sets"] = state.sets
            if state.reps is not None:
                update_data["reps"] = state.reps
            if state.weight is not None:
                update_data["weight"] = state.weight
            if state.rest_time is not None:
                update_data["rest_time"] = state.rest_time
            if state.comments is not None:
                update_data["comments"] = state.comments

            if not update_data:
                state.response = "Cannot update workout: no fields to update. Please specify what to change."
                logger.error("No update data provided")
                return state

            # Convert workout_id to UUID if it's a string
            workout_id_uuid = (
                UUID(state.workout_id)
                if isinstance(state.workout_id, str)
                else state.workout_id
            )

            logger.info(
                f"Attempting to update workout {workout_id_uuid} in database..."
            )

            updated_workout = self.database.update(
                workout_id_uuid, state.user_id, update_data
            )

            if updated_workout:
                logger.info(f"Workout {workout_id_uuid} updated successfully")
                state.response = f"Workout updated! {updated_workout.exercise}: {updated_workout.sets}x{updated_workout.reps} @ {updated_workout.weight}"
            else:
                logger.error(
                    f"Failed to update workout {workout_id_uuid} - not found or access denied"
                )
                state.response = f"Failed to update workout. Workout not found or you don't have permission to update it."

        except ValueError as e:
            logger.error(f"Validation error while updating workout: {e}")
            state.response = f"Cannot update workout: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error while updating workout: {e}", exc_info=True)
            state.response = (
                "An error occurred while updating your workout. Please try again."
            )

        return state

    def _workout_deletor_node(self, state: WorkoutState) -> WorkoutState:
        """Delete workout from database. Requires workout_id."""
        try:
            from uuid import UUID

            if not state.workout_id:
                state.response = "Cannot delete workout: workout ID is required. Please specify which workout to delete."
                logger.error("Workout ID missing for delete operation")
                return state

            # Convert workout_id to UUID if it's a string
            workout_id_uuid = (
                UUID(state.workout_id)
                if isinstance(state.workout_id, str)
                else state.workout_id
            )

            logger.info(
                f"Attempting to delete workout {workout_id_uuid} from database..."
            )

            success = self.database.delete(workout_id_uuid, state.user_id)

            if success:
                logger.info(f"Workout {workout_id_uuid} deleted successfully")
                state.response = f"Workout deleted successfully."
            else:
                logger.error(
                    f"Failed to delete workout {workout_id_uuid} - not found or access denied"
                )
                state.response = f"Failed to delete workout. Workout not found or you don't have permission to delete it."

        except ValueError as e:
            logger.error(f"Validation error while deleting workout: {e}")
            state.response = f"Cannot delete workout: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error while deleting workout: {e}", exc_info=True)
            state.response = (
                "An error occurred while deleting your workout. Please try again."
            )

        return state

    def _handle_error(self, state):
        pass

    def run(self, state: WorkoutState) -> WorkoutState:
        """
        Run the workout graph with the given state using the compiled graph.

        Args:
            state: Initial WorkoutState with user input and intent

        Returns:
            Final WorkoutState after graph execution
        """
        logger.info(f"Running workout graph with intent: {state.intent}")
        # Convert state to dict for graph.invoke()
        state_dict = (
            state.model_dump() if hasattr(state, "model_dump") else state.dict()
        )
        result_dict = self.graph.invoke(state_dict)
        # Convert result back to WorkoutState
        result = WorkoutState(**result_dict)
        logger.info(f"Graph execution completed. Response: {result.response}")
        return result


if __name__ == "__main__":
    workout_graph = WorkoutGraph()
    state = WorkoutState(user_input="", user_id="test_user")

    logger.info("Workout Graph Test - Type 'exit' to quit")

    while True:
        user_input = input("Ask your question: ").strip()

        if user_input.lower() in ["exit", "quit", "q"]:
            logger.info("Exiting workout graph")
            break

        if not user_input:
            continue

        # Update state with new user input
        state.user_input = user_input

        # Run the graph
        state = workout_graph.run(state)

        logger.info("=" * 50)
