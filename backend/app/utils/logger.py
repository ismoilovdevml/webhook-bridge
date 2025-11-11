"""Logging configuration for webhook bridge."""

import logging
import sys
import re
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

# Sensitive data patterns to redact
SENSITIVE_PATTERNS = [
    (re.compile(
        r'(bot_token["\']?\s*[=:]\s*["\']?)([^"\'}\s,]+)', re.I),
        r'\1***REDACTED***'),
    (re.compile(
        r'(webhook_url["\']?\s*[=:]\s*["\']?)(https?://[^"\'}\s,]+)', re.I),
        r'\1***REDACTED_URL***'),
    (re.compile(
        r'(password["\']?\s*[=:]\s*["\']?)([^"\'}\s,]+)', re.I),
        r'\1***REDACTED***'),
    (re.compile(
        r'(secret["\']?\s*[=:]\s*["\']?)([^"\'}\s,]+)', re.I),
        r'\1***REDACTED***'),
    (re.compile(
        r'(api_key["\']?\s*[=:]\s*["\']?)([^"\'}\s,]+)', re.I),
        r'\1***REDACTED***'),
    (re.compile(
        r'(token["\']?\s*[=:]\s*["\']?)([^"\'}\s,]+)', re.I),
        r'\1***REDACTED***'),
    (re.compile(
        r'(authorization["\']?\s*[=:]\s*["\']?)(Bearer\s+[^"\'}\s,]+)',
        re.I),
        r'\1Bearer ***REDACTED***'),
]


class SensitiveDataFilter(logging.Filter):
    """Filter to redact sensitive data from logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Redact sensitive data from log message."""
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            # Apply all sensitive patterns
            message = record.msg
            for pattern, replacement in SENSITIVE_PATTERNS:
                message = pattern.sub(replacement, message)
            record.msg = message

        # Also check args if present
        if hasattr(record, 'args') and record.args:
            cleaned_args = []
            for arg in record.args if isinstance(record.args, tuple) else [record.args]:
                if isinstance(arg, str):
                    for pattern, replacement in SENSITIVE_PATTERNS:
                        arg = pattern.sub(replacement, arg)
                cleaned_args.append(arg)
            record.args = tuple(cleaned_args) if isinstance(record.args, tuple) else cleaned_args[0]

        return True


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

    # Add sensitive data filter
    sensitive_filter = SensitiveDataFilter()
    console_handler.addFilter(sensitive_filter)

    # Format for logs
    if json_logs:
        # JSON format for production
        log_format = (
            '{"time":"%(asctime)s","level":"%(levelname)s",'
            '"name":"%(name)s","message":"%(message)s"}'
        )
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
