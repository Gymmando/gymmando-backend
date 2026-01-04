"""Logging utility module.

This module provides a Logger class for configuring and managing application
logging with both file and console handlers.
"""

import logging
from pathlib import Path


class Logger:
    """Encapsulates logging configuration and provides a logger instance.

    Configures Python logging with both file and console handlers. Logs are
    written to a file in the logs directory and also output to the console.

    Attributes
    ----------
    log_file : Path
        Path to the log file (default: logs/app.log).
    logger : logging.Logger
        Configured logger instance.

    Examples
    --------
    >>> logger = Logger()
    >>> log = logger.get_logger()
    >>> log.info("Application started")
    """

    def __init__(self, name="chat_app", log_file=None):
        """Initialize the Logger with configuration.

        Sets up logging with INFO level, creates logs directory if needed,
        and configures both file and console handlers.

        Parameters
        ----------
        name : str, optional
            Logger name (default: "chat_app").
        log_file : Path, optional
            Path to log file. If None, uses logs/app.log relative to the
            module's parent directory.
        """
        LOG_DIR = Path(__file__).parent.parent / "logs"
        LOG_DIR.mkdir(exist_ok=True)
        self.log_file = log_file or (LOG_DIR / "app.log")

        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            handlers=[logging.FileHandler(self.log_file), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(name)

    def get_logger(self):
        """Get the configured logger instance.

        Returns
        -------
        logging.Logger
            Configured logger instance ready for use.
        """
        return self.logger
