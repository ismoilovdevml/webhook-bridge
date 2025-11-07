"""Logging configuration for webhook bridge."""

import logging
import sys
from typing import Optional

# ANSI color codes for terminal output
COLORS = {
    "DEBUG": "\033[36m",  # Cyan
    "INFO": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",  # Red
    "CRITICAL": "\033[35m",  # Magenta
    "RESET": "\033[0m",  # Reset
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        log_color = COLORS.get(record.levelname, COLORS["RESET"])
        reset_color = COLORS["RESET"]

        # Add color to level name
        record.levelname = f"{log_color}{record.levelname}{reset_color}"

        return super().format(record)


def setup_logging(level: str = "INFO", json_logs: bool = False) -> None:
    """
    Setup logging configuration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Whether to output logs in JSON format
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Format for logs
    if json_logs:
        # JSON format for production
        log_format = '{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}'
        formatter = logging.Formatter(log_format)
    else:
        # Human-readable format for development
        log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        formatter = ColoredFormatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = []
    root_logger.addHandler(console_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name or __name__)
