"""Retry logic with exponential backoff."""

import asyncio
from typing import Callable, TypeVar, Any
from ..config import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


async def retry_with_backoff(
    func: Callable[[], Any],
    max_attempts: int = None,
    initial_delay: float = None,
    max_delay: float = None,
    exponential_base: float = None,
    description: str = "operation",
) -> tuple[bool, Any]:
    """
    Retry an async function with exponential backoff.

    Args:
        func: Async function to retry
        max_attempts: Maximum retry attempts (default from settings)
        initial_delay: Initial delay in seconds (default from settings)
        max_delay: Maximum delay in seconds (default from settings)
        exponential_base: Base for exponential backoff (default from settings)
        description: Description of operation for logging

    Returns:
        Tuple of (success: bool, result: Any)
    """
    if not settings.RETRY_ENABLED:
        try:
            result = await func()
            return (True, result)
        except Exception as e:
            logger.error(f"Failed to execute {description}: {e}")
            return (False, None)

    max_attempts = max_attempts or settings.RETRY_MAX_ATTEMPTS
    initial_delay = initial_delay or settings.RETRY_INITIAL_DELAY
    max_delay = max_delay or settings.RETRY_MAX_DELAY
    exponential_base = exponential_base or settings.RETRY_EXPONENTIAL_BASE

    last_exception = None

    for attempt in range(1, max_attempts + 1):
        try:
            result = await func()
            if attempt > 1:
                logger.info(
                    f"Successfully executed {description} on attempt {attempt}"
                )
            return (True, result)

        except Exception as e:
            last_exception = e
            if attempt < max_attempts:
                # Calculate delay with exponential backoff
                delay = min(
                    initial_delay * (exponential_base ** (attempt - 1)), max_delay
                )
                logger.warning(
                    f"Failed {description} (attempt {attempt}/{max_attempts}): "
                    f"{str(e)}. Retrying in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    f"Failed {description} after {max_attempts} attempts: {str(e)}"
                )

    return (False, last_exception)
