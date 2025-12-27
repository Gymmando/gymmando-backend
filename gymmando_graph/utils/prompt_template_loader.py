"""Module for loading prompt templates from markdown files.

This module provides functionality to load prompt templates stored as markdown
files for use in chat agents and other LLM applications.
"""

from pathlib import Path

from .logger import Logger

# Lazy-load logger to avoid slow initialization at import time
_logger = None


def _get_logger():
    global _logger
    if _logger is None:
        _logger = Logger().get_logger()
    return _logger


class PromptTemplateLoader:
    """Loads prompt templates from markdown files.

    Attributes:
        prompt_template_directory: Path to the directory containing prompt templates.
    """

    def __init__(self, templates_directory: str):
        """Initialize the PromptTemplateLoader with a directory path.

        Args:
            template_directory: Path to the directory containing prompt templates.
        """
        self.templates_directory = Path(templates_directory)

    def load_template(self, file_name: str) -> str:
        """Loads a prompt template from a markdown file.

        Args:
            file_name: Name of the markdown file to load.

        Returns:
            The content of the template file as a string.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            PermissionError: If there are insufficient permissions to read the file.
            Exception: For any other unexpected errors during file reading.
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
