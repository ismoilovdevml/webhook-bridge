"""Base provider interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict
from ..utils.logger import get_logger
from ..utils.exceptions import ConfigurationError

logger = get_logger(__name__)


class BaseProvider(ABC):
    """Base class for all notification providers."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize provider with configuration.

        Args:
            config: Provider configuration dictionary

        Raises:
            ConfigurationError: If configuration is invalid
        """
        self.config = config
        self._validate_config()
        logger.info(f"Initialized {self.__class__.__name__}")

    @abstractmethod
    def _validate_config(self) -> None:
        """
        Validate provider configuration.

        Raises:
            ConfigurationError: If configuration is invalid
        """
        pass

    @abstractmethod
    async def send(self, message: Dict[str, Any]) -> bool:
        """
        Send notification message.

        Args:
            message: Formatted message to send

        Returns:
            True if sent successfully, False otherwise

        Raises:
            ProviderError: If sending fails
        """
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Test provider connection.

        Returns:
            True if connection is successful, False otherwise
        """
        pass

    def _get_required_field(self, field: str) -> Any:
        """
        Get required field from config.

        Args:
            field: Field name

        Returns:
            Field value

        Raises:
            ConfigurationError: If field is missing
        """
        value = self.config.get(field)
        if not value:
            raise ConfigurationError(
                f"Missing required field: {field}",
                details={"provider": self.__class__.__name__, "field": field},
            )
        return value

    def _get_optional_field(self, field: str, default: Any = None) -> Any:
        """
        Get optional field from config.

        Args:
            field: Field name
            default: Default value if field is missing

        Returns:
            Field value or default
        """
        return self.config.get(field, default)
