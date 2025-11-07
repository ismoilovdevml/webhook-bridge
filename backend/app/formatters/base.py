"""Base formatter interface for all message formatters."""

from abc import ABC, abstractmethod
from typing import Any, Dict
from ..parsers.base import ParsedEvent


class BaseFormatter(ABC):
    """Base class for all message formatters."""

    @abstractmethod
    def format(self, event: ParsedEvent) -> Dict[str, Any]:
        """
        Format a parsed event into platform-specific message format.

        Args:
            event: Parsed event data

        Returns:
            Formatted message ready to send to the platform
        """
        pass

    def _get_event_emoji(self, event_type: str) -> str:
        """
        Get emoji for event type.

        Args:
            event_type: Type of event

        Returns:
            Emoji string
        """
        emoji_map = {
            "push": "📤",
            "pull_request": "🔀",
            "merge_request": "🔀",
            "pipeline": "🔧",
            "workflow_run": "🔧",
            "issues": "🐛",
            "issue": "🐛",
            "comment": "💬",
            "note": "💬",
            "tag_push": "🏷️",
            "release": "🚀",
            "wiki": "📝",
        }
        return emoji_map.get(event_type, "📋")

    def _get_status_emoji(self, status: str) -> str:
        """
        Get emoji for status.

        Args:
            status: Status string

        Returns:
            Emoji string
        """
        status_lower = status.lower()
        emoji_map = {
            "success": "✅",
            "passed": "✅",
            "failed": "❌",
            "failure": "❌",
            "error": "❌",
            "running": "⏳",
            "pending": "⏳",
            "canceled": "🚫",
            "cancelled": "🚫",
            "skipped": "⏭️",
            "merged": "✅",
            "opened": "🔓",
            "closed": "🔒",
            "updated": "📝",
        }
        return emoji_map.get(status_lower, "ℹ️")

    def _truncate(self, text: str, max_length: int = 200) -> str:
        """
        Truncate text to max length.

        Args:
            text: Text to truncate
            max_length: Maximum length

        Returns:
            Truncated text
        """
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
