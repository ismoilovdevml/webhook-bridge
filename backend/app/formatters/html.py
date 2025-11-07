"""HTML formatter for Telegram."""

from typing import Any, Dict
from .base import BaseFormatter
from ..parsers.base import ParsedEvent


class HTMLFormatter(BaseFormatter):
    """Format messages in HTML format for Telegram."""

    def format(self, event: ParsedEvent) -> Dict[str, Any]:
        """
        Format event as HTML message.

        Args:
            event: Parsed event

        Returns:
            Dictionary with 'text' and 'parse_mode' keys
        """
        emoji = self._get_event_emoji(event.event_type)

        # Build message parts
        lines = [
            f"<b>{emoji} {event.event_type.replace('_', ' ').title()}</b>",
            "",
            f"<b>Project:</b> {self._escape_html(event.project)}",
            f"<b>Author:</b> {self._escape_html(event.author)}",
        ]

        # Add branch if present
        if event.branch:
            lines.append(f"<b>Branch:</b> <code>{self._escape_html(event.branch)}</code>")

        # Add specific event data
        if event.event_type == "push" and event.commits:
            lines.extend(["", f"<b>Commits:</b> {len(event.commits)}"])
            for commit in event.commits[:3]:  # Show first 3 commits
                commit_id = commit.get("id", "")[:8]
                msg = self._escape_html(self._truncate(commit.get("message", ""), 80))
                lines.append(f"• <code>{commit_id}</code> {msg}")
            if len(event.commits) > 3:
                lines.append(f"• ... and {len(event.commits) - 3} more")

        elif event.event_type in ["merge_request", "pull_request"]:
            mr_data = event.data
            status = mr_data.get("status", "opened")
            status_emoji = self._get_status_emoji(status)
            title = self._escape_html(mr_data.get("title", "N/A"))
            lines.extend([
                f"<b>Status:</b> {status_emoji} {status.title()}",
                f"<b>Title:</b> {title}",
            ])
            if mr_data.get("source_branch") and mr_data.get("target_branch"):
                src = self._escape_html(mr_data["source_branch"])
                tgt = self._escape_html(mr_data["target_branch"])
                lines.append(f"<b>Merge:</b> <code>{src}</code> → <code>{tgt}</code>")

        elif event.event_type in ["pipeline", "workflow_run"]:
            pipeline_data = event.data
            status = pipeline_data.get("status", "unknown")
            status_emoji = self._get_status_emoji(status)
            lines.extend([
                f"<b>Status:</b> {status_emoji} {status.upper()}",
            ])
            if pipeline_data.get("duration"):
                duration = pipeline_data["duration"]
                lines.append(f"<b>Duration:</b> {duration}s")
            if pipeline_data.get("stages"):
                stages = pipeline_data["stages"]
                lines.append(f"<b>Stages:</b> {', '.join(stages)}")

        elif event.event_type in ["issue", "issues"]:
            issue_data = event.data
            status = issue_data.get("action", "opened")
            status_emoji = self._get_status_emoji(status)
            title = self._escape_html(issue_data.get("title", "N/A"))
            lines.extend([
                f"<b>Action:</b> {status_emoji} {status.title()}",
                f"<b>Title:</b> {title}",
            ])

        elif event.event_type in ["comment", "note"]:
            comment_data = event.data
            comment_body = self._escape_html(
                self._truncate(comment_data.get("body", ""), 150)
            )
            noteable_type = self._escape_html(comment_data.get("noteable_type", "Unknown"))
            lines.extend([
                f"<b>Comment on:</b> {noteable_type}",
                f"<b>Comment:</b> {comment_body}",
            ])

        elif event.event_type == "release":
            release_data = event.data
            tag = self._escape_html(release_data.get("tag", "N/A"))
            name = self._escape_html(release_data.get("name", "N/A"))
            lines.extend([
                f"<b>Tag:</b> <code>{tag}</code>",
                f"<b>Name:</b> {name}",
            ])

        # Add URL as link if present
        if event.url:
            lines.extend(["", f"<a href=\"{event.url}\">View Details</a>"])

        return {
            "text": "\n".join(lines),
            "parse_mode": "HTML"
        }

    def _escape_html(self, text: str) -> str:
        """
        Escape HTML special characters.

        Args:
            text: Text to escape

        Returns:
            Escaped text
        """
        if not text:
            return ""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
