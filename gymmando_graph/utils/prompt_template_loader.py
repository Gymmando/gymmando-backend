"""Module for loading prompt templates from markdown files.

This module provides functionality to load prompt templates stored as markdown
files for use in chat agents and other LLM applications.
"""

from pathlib import Path

from .logger import Logger

# Lazy-load logger to avoid slow initialization at import time
_logger = None


def _get_logger():
    """Get or create the logger instance (lazy loading).

    Returns
    -------
    logging.Logger
        Logger instance for this module.
    """
    global _logger
    if _logger is None:
        _logger = Logger().get_logger()
    return _logger


class PromptTemplateLoader:
    """Loads prompt templates from markdown files.

    Provides functionality to load and read prompt template files stored as
    markdown. Templates are loaded from a specified directory and returned
    as strings for use in LangChain prompts.

    Attributes
    ----------
    templates_directory : Path
        Path to the directory containing prompt templates.

    Examples
    --------
    >>> loader = PromptTemplateLoader("/path/to/templates")
    >>> template = loader.load_template("system_prompt.md")
    """

    def __init__(self, templates_directory: str):
        """Initialize the PromptTemplateLoader with a directory path.

        Parameters
        ----------
        templates_directory : str
            Path to the directory containing prompt templates.
        """
        self.templates_directory = Path(templates_directory)

    def load_template(self, file_name: str) -> str:
        """Load a prompt template from a markdown file.

        Reads the specified markdown file from the templates directory and
        returns its content as a string.

        Parameters
        ----------
        file_name : str
            Name of the markdown file to load (e.g., "system_prompt.md").

        Returns
        -------
        str
            The content of the template file as a string.

        Raises
        ------
        FileNotFoundError
            If the specified file does not exist in the templates directory.
        PermissionError
            If there are insufficient permissions to read the file.
        Exception
            For any other unexpected errors during file reading.
        """
        try:
            file_path = self.templates_directory / file_name
            return file_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            _get_logger().error(f"File not found: {file_path}")
            raise
        except PermissionError:
            _get_logger().error(f"Permission denied: {file_path}")
            raise
        except Exception as e:
            _get_logger().error(f"Unexpected error loading template: {file_path} - {e}")
            raise
