"""Slack Block Kit formatter."""

from typing import Any, Dict, List
from .base import BaseFormatter
from ..parsers.base import ParsedEvent


class SlackBlocksFormatter(BaseFormatter):
    """Format messages using Slack Block Kit."""

    def format(self, event: ParsedEvent) -> Dict[str, Any]:
        """
        Format event as Slack Block Kit message.

        Args:
            event: Parsed event

        Returns:
            Dictionary with 'blocks' and 'text' keys
        """
        emoji = self._get_event_emoji(event.event_type)
        blocks: List[Dict[str, Any]] = []

        # Header block
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{emoji} {event.event_type.replace('_', ' ').title()}",
                "emoji": True
            }
        })

        # Main info section
        fields: List[Dict[str, Any]] = [
            {
                "type": "mrkdwn",
                "text": f"*Project:*\n{event.project}"
            },
            {
                "type": "mrkdwn",
                "text": f"*Author:*\n{event.author}"
            }
        ]

        if event.branch:
            fields.append({
                "type": "mrkdwn",
                "text": f"*Branch:*\n`{event.branch}`"
            })

        blocks.append({
            "type": "section",
            "fields": fields
        })

        # Event-specific sections
        if event.event_type == "push" and event.commits:
            commit_lines = [f"*Commits:* {len(event.commits)}"]
            for commit in event.commits[:3]:
                commit_id = commit.get("id", "")[:8]
                msg = self._truncate(commit.get("message", ""), 80)
                commit_lines.append(f"• `{commit_id}` {msg}")
            if len(event.commits) > 3:
                commit_lines.append(f"• ... and {len(event.commits) - 3} more")

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "\n".join(commit_lines)
                }
            })

        elif event.event_type in ["merge_request", "pull_request"]:
            mr_data = event.data
            status = mr_data.get("status", "opened")
            status_emoji = self._get_status_emoji(status)

            mr_fields: List[Dict[str, Any]] = [
                {
                    "type": "mrkdwn",
                    "text": f"*Status:*\n{status_emoji} {status.title()}"
                }
            ]

            if mr_data.get("source_branch") and mr_data.get("target_branch"):
                mr_fields.append({
                    "type": "mrkdwn",
                    "text": f"*Merge:*\n`{mr_data['source_branch']}` → `{mr_data['target_branch']}`"
                })

            blocks.append({
                "type": "section",
                "fields": mr_fields
            })

            if mr_data.get("title"):
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Title:*\n{mr_data['title']}"
                    }
                })

        elif event.event_type in ["pipeline", "workflow_run"]:
            pipeline_data = event.data
            status = pipeline_data.get("status", "unknown")
            status_emoji = self._get_status_emoji(status)

            pipeline_fields: List[Dict[str, Any]] = [
                {
                    "type": "mrkdwn",
                    "text": f"*Status:*\n{status_emoji} {status.upper()}"
                }
            ]

            if pipeline_data.get("duration"):
                pipeline_fields.append({
                    "type": "mrkdwn",
                    "text": f"*Duration:*\n{pipeline_data['duration']}s"
                })

            blocks.append({
                "type": "section",
                "fields": pipeline_fields
            })

            if pipeline_data.get("stages"):
                stages_text = ", ".join(pipeline_data["stages"])
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Stages:*\n{stages_text}"
                    }
                })

        elif event.event_type in ["issue", "issues"]:
            issue_data = event.data
            status = issue_data.get("action", "opened")
            status_emoji = self._get_status_emoji(status)

            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Action:*\n{status_emoji} {status.title()}"
                    }
                ]
            })

            if issue_data.get("title"):
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Title:*\n{issue_data['title']}"
                    }
                })

        elif event.event_type in ["comment", "note"]:
            comment_data = event.data
            comment_body = self._truncate(comment_data.get("body", ""), 150)

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Comment on:* {comment_data.get('noteable_type', 'Unknown')}\n\n{comment_body}"
                }
            })

        # Add button with URL if present
        if event.url:
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Details",
                            "emoji": True
                        },
                        "url": event.url,
                        "style": "primary"
                    }
                ]
            })

        # Fallback text for notifications
        fallback_text = f"{emoji} {event.event_type.replace('_', ' ').title()} in {event.project} by {event.author}"

        return {
            "blocks": blocks,
            "text": fallback_text  # Fallback for notifications
        }
