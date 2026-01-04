"""Workout parser agent module.

This module provides an LLM-based agent for parsing natural language user input
into structured workout data using LangChain and OpenAI.
"""

from pathlib import Path
from typing import cast

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_openai import ChatOpenAI

from gymmando_graph.modules.workout.schemas import WorkoutParserResponse
from gymmando_graph.utils import PromptTemplateLoader

load_dotenv()


class WorkoutParser:
    """Agent for parsing natural language workout input into structured data.

    Uses an LLM (OpenAI GPT-4o-mini) with structured output parsing to extract
    workout information from user input. The parser identifies exercise name,
    sets, reps, weight, rest time, comments, and workout_id when present.

    Attributes
    ----------
    parser : PydanticOutputParser
        Parser that converts LLM output to WorkoutParserResponse model.
    prompt : ChatPromptTemplate
        LangChain prompt template combining system and human messages.
    llm : ChatOpenAI
        OpenAI LLM instance configured for structured output.
    chain : Chain
        LangChain chain combining prompt, LLM, and parser.

    Examples
    --------
    >>> parser = WorkoutParser()
    >>> result = parser.process("Squats 3 sets of 10 reps at 135 lbs")
    >>> print(result.exercise, result.sets, result.reps, result.weight)
    """

    def __init__(self):
        """Initialize the WorkoutParser with LLM chain and prompt templates.

        Loads prompt templates from markdown files, initializes the Pydantic
        output parser, creates the LangChain prompt template, and sets up
        the LLM chain for processing user input.
        """
        # define the parser
        self.parser = PydanticOutputParser(pydantic_object=WorkoutParserResponse)
        format_instructions = self.parser.get_format_instructions()

        # initialize the prompt
        # Get the prompt templates directory relative to this file
        prompts_dir = Path(__file__).parent.parent / "prompt_templates"
        ptl = PromptTemplateLoader(str(prompts_dir))
        system_template = ptl.load_template("workout_parser_prompt_template_system.md")
        human_template = ptl.load_template("workout_parser_prompt_template_human.md")
        system_message = SystemMessagePromptTemplate.from_template(
            template=system_template
        )
        human_message = HumanMessagePromptTemplate.from_template(
            template=human_template, input_variables=["user_input"]
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [system_message, human_message]
        ).partial(format_instructions=format_instructions)

        # initialize the LLM (OpenAI)
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
        )

        # create the chain
        self.chain = self.prompt | self.llm | self.parser

    def show_prompt(self, user_input: str):
        """Format and return the prompt template with user input.

        Useful for debugging and inspecting the exact prompt sent to the LLM.

        Parameters
        ----------
        user_input : str
            User input text to format into the prompt.

        Returns
        -------
        str
            Formatted prompt string ready for LLM consumption.
        """
        return self.prompt.format(user_input=user_input)

    def process(self, user_input: str) -> WorkoutParserResponse:
        """Process user input through the LLM chain and return parsed response.

        Invokes the LangChain chain (prompt -> LLM -> parser) to extract
        structured workout data from natural language input.

        Parameters
        ----------
        user_input : str
            Natural language input describing a workout (e.g., "Squats 3x10 @ 135 lbs").

        Returns
        -------
        WorkoutParserResponse
            Structured response containing extracted workout fields:
            exercise, sets, reps, weight, rest_time, comments, workout_id.

        Notes
        -----
        The LLM is configured with temperature=0 for consistent, deterministic
        parsing results. The output is validated against the WorkoutParserResponse
        Pydantic model.
        """
        response = self.chain.invoke({"user_input": user_input})
        return cast(WorkoutParserResponse, response)


if __name__ == "__main__":
    parser = WorkoutParser()
    result = parser.process("Squats 20 reps, 3 sets and for 20 minutes?")
    print(result.model_dump_json(indent=2))
