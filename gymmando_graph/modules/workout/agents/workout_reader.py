"""Workout reader agent module.

This module provides an LLM-based agent for reading and retrieving workout
data from the database using natural language queries. The agent uses tools
to query the database based on user intent.
"""

import json
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI

from gymmando_graph.modules.workout.crud import WorkoutCRUD
from gymmando_graph.utils import Logger, PromptTemplateLoader

load_dotenv()

logger = Logger().get_logger()

# Initialize WorkoutCRUD instance
_workout_crud = WorkoutCRUD()


def _query_workouts_impl(
    user_id: str,
    exercise: Optional[str] = None,
    exercise_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: Optional[int] = 10,
    order_by: Optional[str] = "created_at",
    order_direction: Optional[str] = "desc",
) -> str:
    """Query workouts from the database based on various filters.

    Implementation function for the query_workouts tool. Queries the database
    using WorkoutCRUD and returns results as a JSON string for LLM consumption.

    Parameters
    ----------
    user_id : str
        The user ID to filter workouts by (required).
    exercise : Optional[str], optional
        Filter by specific exercise name (e.g., "squats", "bench press").
        Uses case-insensitive partial matching.
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
    str
        JSON string representation of workout data matching the query.
        Returns empty array JSON if no workouts found, or error JSON on failure.

    Notes
    -----
    This function is wrapped as a LangChain StructuredTool for use by the
    WorkoutReader agent. Errors are caught and returned as JSON error objects
    rather than raising exceptions.
    """
    try:
        logger.info(
            f"🔍 Querying workouts from Supabase with params: user_id={user_id}, exercise={exercise}, limit={limit}"
        )

        # Use WorkoutCRUD to query workouts
        workouts = _workout_crud.query(
            user_id=user_id,
            exercise=exercise,
            exercise_type=exercise_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            order_by=order_by,
            order_direction=order_direction,
        )

        logger.info(f"Query returned {len(workouts)} workouts")

        if workouts:
            # Convert to JSON string for LLM consumption
            workouts_dict = [workout.model_dump() for workout in workouts]
            return json.dumps(workouts_dict, default=str)

        return json.dumps([])

    except Exception as e:
        logger.error(f"Failed to query workouts: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


# Create the LangChain tool
query_workouts = StructuredTool.from_function(
    func=_query_workouts_impl,
    name="query_workouts",
    description="Query workouts from the database based on various filters. Use this to retrieve workout history for users.",
)


class WorkoutReader:
    """Agent for reading and retrieving workout data using natural language queries.

    Uses an LLM with tools to interpret user queries and retrieve relevant
    workout records from the database. The agent can understand complex queries
    like "show me my last 5 squats workouts" and translate them into database
    queries.

    Attributes
    ----------
    prompt : ChatPromptTemplate
        LangChain prompt template for the reader agent.
    llm : ChatOpenAI
        OpenAI LLM instance configured for tool use.
    tools : list[StructuredTool]
        List of available tools (query_workouts).
    llm_with_tools : ChatOpenAI
        LLM instance bound with tools for function calling.

    Examples
    --------
    >>> reader = WorkoutReader()
    >>> result = reader.retrieve("Show me my last 3 squats workouts", "user123")
    >>> print(result)  # JSON string of workout data
    """

    def __init__(self):
        """Initialize the WorkoutReader with LLM, tools, and prompt templates.

        Loads prompt templates from markdown files, initializes the OpenAI LLM,
        and binds the query_workouts tool for function calling.
        """
        # Initialize the prompt
        # Get the prompt templates directory relative to this file
        prompts_dir = Path(__file__).parent.parent / "prompt_templates"
        ptl = PromptTemplateLoader(str(prompts_dir))
        system_template = ptl.load_template("workout_reader_prompt_template_system.md")
        human_template = ptl.load_template("workout_reader_prompt_template_human.md")
        system_message = SystemMessagePromptTemplate.from_template(
            template=system_template
        )
        human_message = HumanMessagePromptTemplate.from_template(
            template=human_template, input_variables=["user_query", "user_id"]
        )

        self.prompt = ChatPromptTemplate.from_messages([system_message, human_message])

        # Initialize the LLM with tools
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.tools = [query_workouts]
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def retrieve(self, user_query: str, user_id: str) -> str:
        """Process a user query and retrieve relevant workout data.

        Uses the LLM with tools to interpret the natural language query,
        call the query_workouts tool with appropriate parameters, and return
        the results directly as JSON.

        Parameters
        ----------
        user_query : str
            Natural language query from the user (e.g., "show me my last 5 squats").
        user_id : str
            User ID to filter workouts by (automatically added to tool calls).

        Returns
        -------
        str
            JSON string representation of workout data matching the query.
            If no tool call is detected, returns the LLM's text response.

        Notes
        -----
        The method performs a single LLM call with tool binding. If the LLM
        decides to call the query_workouts tool, the tool result is returned
        directly without a second LLM call for formatting.
        """
        from gymmando_graph.utils import Logger

        logger = Logger().get_logger()

        # Format the prompt
        messages = list(
            self.prompt.format_messages(user_query=user_query, user_id=user_id)
        )

        # Get LLM response with tool calls
        response = self.llm_with_tools.invoke(messages)

        logger.info(f"LLM response: {response}")
        logger.info(f"Tool calls: {getattr(response, 'tool_calls', None)}")

        # Check if LLM wants to call a tool
        if hasattr(response, "tool_calls") and response.tool_calls:
            # Execute tool calls
            for tool_call in response.tool_calls:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args", {})
                tool_args["user_id"] = user_id  # Always add user_id

                logger.info(f"Calling tool: {tool_name} with args: {tool_args}")

                # Call the tool and return result directly
                if tool_name == "query_workouts":
                    tool_result = query_workouts.invoke(tool_args)
                    logger.info(f"Tool result: {tool_result}")
                    return str(tool_result)

        # If no tool call, return LLM response
        logger.warning("No tool call detected in LLM response")
        if hasattr(response, "content") and response.content:
            return str(response.content)
        return str(response)


if __name__ == "__main__":
    from gymmando_graph.database import get_supabase_client

    # First, let's check what's actually in the database
    print("=" * 60)
    print("Checking database contents...")
    print("=" * 60)
    client = get_supabase_client()

    # Get all workouts to see what user_ids and exercises exist
    all_workouts = client.table("workouts").select("*").limit(20).execute()
    print(f"Total workouts in DB: {len(all_workouts.data)}")
    if all_workouts.data:
        print("\nSample workouts:")
        for workout in all_workouts.data[:5]:
            print(
                f"  - user_id: {workout.get('user_id')}, exercise: {workout.get('exercise')}, created: {workout.get('created_at')}"
            )
    print("=" * 60)
    print()

    # Now test the agent
    agent = WorkoutReader()

    # Test 1: Check if any workouts exist for the user (no exercise filter)
    print("Test 1: Getting any workouts for user...")
    result = agent.retrieve("Show me my workouts", user_id="default_user")
    print(f"Result: {result}\n")

    # Test 2: Query with specific exercise
    print("Test 2: Getting last lunges workout...")
    result = agent.retrieve(
        "What was my last 2 lunges workout?", user_id="default_user"
    )
    print(f"Result: {result}")
