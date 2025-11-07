"""Tests for message formatters."""
import pytest
from app.formatters.html import HTMLFormatter
from app.formatters.markdown import MarkdownFormatter
from app.parsers.base import ParsedEvent


class TestHTMLFormatter:
    """Test HTML formatter."""

    def test_format_push_event(self):
        """Test formatting push event as HTML."""
        formatter = HTMLFormatter()
        event = ParsedEvent(
            platform="gitlab",
            event_type="push",
            project="test/project",
            project_url="https://example.com/test/project",
            author="Test User",
            author_username="testuser",
            ref="main",
            commits=[{"id": "abc123", "message": "Test commit"}],
            commit_count=1
        )

        result = formatter.format(event)

        assert "text" in result
        assert "parse_mode" in result
        assert result["parse_mode"] == "HTML"
        assert "test/project" in result["text"]
        assert "Test User" in result["text"]


class TestMarkdownFormatter:
    """Test Markdown formatter."""

    def test_format_push_event(self):
        """Test formatting push event as Markdown."""
        formatter = MarkdownFormatter()
        event = ParsedEvent(
            platform="gitlab",
            event_type="push",
            project="test/project",
            project_url="https://example.com/test/project",
            author="Test User",
            author_username="testuser",
            ref="main",
            commits=[{"id": "abc123", "message": "Test commit"}],
            commit_count=1
        )

        result = formatter.format(event)

        assert "text" in result
        assert "test/project" in result["text"]
        assert "Test User" in result["text"]
        assert "**" in result["text"]  # Markdown bold
