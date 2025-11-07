"""Markdown formatter for Mattermost and similar platforms."""

from typing import Any, Dict
from .base import BaseFormatter
from ..parsers.base import ParsedEvent


class MarkdownFormatter(BaseFormatter):
    """Format messages in Markdown format for Mattermost."""

    def format(self, event: ParsedEvent) -> Dict[str, Any]:
        """
        Format event as Markdown message.

        Args:
            event: Parsed event

        Returns:
            Dictionary with 'text' key containing markdown message
        """
        emoji = self._get_event_emoji(event.event_type)

        # Build message parts
        lines = [
            f"### {emoji} {event.event_type.replace('_', ' ').title()}",
            "",
            f"**Project:** {event.project}",
            f"**Author:** {event.author}",
        ]

        # Add branch if present
        if event.branch:
            lines.append(f"**Branch:** `{event.branch}`")

        # Add specific event data
        if event.event_type == "push" and event.commits:
            lines.extend(["", f"**Commits:** {len(event.commits)}"])
            for commit in event.commits[:3]:  # Show first 3 commits
                msg = self._truncate(commit.get("message", ""), 80)
                lines.append(f"- `{commit.get('id', '')[:8]}` {msg}")
            if len(event.commits) > 3:
                lines.append(f"- ... and {len(event.commits) - 3} more")

        elif event.event_type in ["merge_request", "pull_request"]:
            mr_data = event.data
            status = mr_data.get("status", "opened")
            status_emoji = self._get_status_emoji(status)
            lines.extend([
                f"**Status:** {status_emoji} {status.title()}",
                f"**Title:** {mr_data.get('title', 'N/A')}",
            ])
            if mr_data.get("source_branch") and mr_data.get("target_branch"):
                lines.append(
                    f"**Merge:** `{mr_data['source_branch']}` → `{mr_data['target_branch']}`"
                )

        elif event.event_type in ["pipeline", "workflow_run"]:
            pipeline_data = event.data
            status = pipeline_data.get("status", "unknown")
            status_emoji = self._get_status_emoji(status)
            lines.extend([
                f"**Status:** {status_emoji} {status.upper()}",
            ])
            if pipeline_data.get("duration"):
                duration = pipeline_data["duration"]
                lines.append(f"**Duration:** {duration}s")

        elif event.event_type in ["issue", "issues"]:
            issue_data = event.data
            status = issue_data.get("action", "opened")
            status_emoji = self._get_status_emoji(status)
            lines.extend([
                f"**Action:** {status_emoji} {status.title()}",
                f"**Title:** {issue_data.get('title', 'N/A')}",
            ])

        elif event.event_type in ["comment", "note"]:
            comment_data = event.data
            comment_body = self._truncate(comment_data.get("body", ""), 150)
            lines.extend([
                f"**Comment on:** {comment_data.get('noteable_type', 'Unknown')}",
                f"**Comment:** {comment_body}",
            ])

        # Add URL if present
        if event.url:
            lines.extend(["", f"[View Details]({event.url})"])

        return {"text": "\n".join(lines)}
