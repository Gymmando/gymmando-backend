from pathlib import Path

from dotenv import load_dotenv
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_groq import ChatGroq

from gymmando_graph.utils import PromptTemplateLoader

load_dotenv()


class Parser:
    def __init__(self):
        # define the parser
        self.parser = None

        # initialize the prompt
        # Get the prompt templates directory relative to this file
        prompts_dir = Path(__file__).parent.parent / "prompt_templates"
        ptl = PromptTemplateLoader(str(prompts_dir))
        system_template = ptl.load_template("parser_prompt_template_system.md")
        human_template = ptl.load_template("parser_prompt_template_human.md")
        system_message = SystemMessagePromptTemplate.from_template(
            template=system_template
        )
        human_message = HumanMessagePromptTemplate.from_template(
            template=human_template, input_variables=["user_input"]
        )

        self.prompt = ChatPromptTemplate.from_messages([system_message, human_message])

        # initialize the LLM
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",  # or "llama-3.3-70b-versatile" for better quality
            temperature=0,
        )

        # create the chain
        self.chain = self.prompt | self.llm

    def show_prompt(self, user_input: str):
        return self.prompt.format(user_input=user_input)

    def process(self, user_input: str):
        """Process user input through the LLM chain."""
        response = self.chain.invoke({"user_input": user_input})
        return response.content


if __name__ == "__main__":
    parser = Parser()
    result = parser.process("Hello")
    print(result)
