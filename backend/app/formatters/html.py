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
        if event.ref:
            lines.append(f"<b>Branch:</b> <code>{self._escape_html(event.ref)}</code>")

        # Add specific event data
        if event.event_type == "push" and event.commits:
            lines.extend(["", f"<b>Commits:</b> {len(event.commits)}"])
            for commit in event.commits[:3]:  # Show first 3 commits
                commit_id = commit.get("id", "")[:8]
                commit_url = commit.get("url", "")
                msg = self._escape_html(self._truncate(commit.get("message", ""), 80))
                if commit_url:
                    lines.append(f'• <a href="{commit_url}"><code>{commit_id}</code></a> {msg}')
                else:
                    lines.append(f"• <code>{commit_id}</code> {msg}")
            if len(event.commits) > 3:
                lines.append(f"• ... and {len(event.commits) - 3} more")

        elif event.event_type in ["merge_request", "pull_request"]:
            status = event.mr_state or event.mr_action or "opened"
            status_emoji = self._get_status_emoji(status)
            title = self._escape_html(event.mr_title or "N/A")

            # Make title clickable if URL exists
            if event.mr_url:
                title_display = f'<a href="{event.mr_url}">{title}</a>'
            else:
                title_display = title

            lines.extend(
                [
                    f"<b>Status:</b> {status_emoji} {status.title()}",
                    f"<b>Title:</b> {title_display}",
                ]
            )
            if event.source_branch and event.target_branch:
                src = self._escape_html(event.source_branch)
                tgt = self._escape_html(event.target_branch)
                lines.append(f"<b>Merge:</b> <code>{src}</code> → <code>{tgt}</code>")

        elif event.event_type in ["pipeline", "workflow_run"]:
            status = event.pipeline_status or "unknown"
            status_emoji = self._get_status_emoji(status)

            # Make pipeline ID clickable if URL exists
            if event.pipeline_id and event.pipeline_url:
                pipeline_link = f'<a href="{event.pipeline_url}">#{event.pipeline_id}</a>'
                lines.append(f"<b>Pipeline:</b> {pipeline_link}")

            lines.append(f"<b>Status:</b> {status_emoji} {status.upper()}")

            if event.pipeline_duration:
                lines.append(f"<b>Duration:</b> {event.pipeline_duration}s")
            if event.pipeline_stages:
                lines.append(f"<b>Stages:</b> {', '.join(event.pipeline_stages)}")

        elif event.event_type in ["issue", "issues"]:
            status = event.issue_action or event.issue_state or "opened"
            status_emoji = self._get_status_emoji(status)
            title = self._escape_html(event.issue_title or "N/A")

            # Make title clickable if URL exists
            if event.issue_url:
                title_display = f'<a href="{event.issue_url}">{title}</a>'
            else:
                title_display = title

            lines.extend(
                [
                    f"<b>Action:</b> {status_emoji} {status.title()}",
                    f"<b>Title:</b> {title_display}",
                ]
            )

            # Add issue number if available
            if event.issue_iid:
                lines.insert(-2, f"<b>Issue:</b> #{event.issue_iid}")

        elif event.event_type in ["comment", "note"]:
            comment_body = self._escape_html(
                self._truncate(event.comment_body or "", 150)
            )
            noteable_type = self._escape_html(
                event.raw_data.get("noteable_type", "Unknown")
            )

            lines.extend([f"<b>Comment on:</b> {noteable_type}"])

            # Make comment clickable if URL exists
            if event.comment_url:
                lines.append(f'<b>Comment:</b> <a href="{event.comment_url}">View comment</a>')
            else:
                lines.append(f"<b>Comment:</b> {comment_body}")

        elif event.event_type == "release":
            tag = self._escape_html(event.release_tag or "N/A")
            name = self._escape_html(event.release_name or "N/A")

            # Make release name clickable if URL exists
            if event.release_url:
                name_display = f'<a href="{event.release_url}">{name}</a>'
            else:
                name_display = name

            lines.extend(
                [
                    f"<b>Tag:</b> <code>{tag}</code>",
                    f"<b>Name:</b> {name_display}",
                ]
            )

            # Add description if available
            if event.release_description:
                desc = self._escape_html(self._truncate(event.release_description, 100))
                lines.append(f"<b>Description:</b> {desc}")

        elif event.event_type == "deployment":
            status = event.deployment_status or "unknown"
            status_emoji = self._get_status_emoji(status)
            environment = self._escape_html(event.deployment_environment or "N/A")

            lines.extend(
                [
                    f"<b>Environment:</b> {environment}",
                    f"<b>Status:</b> {status_emoji} {status.title()}",
                ]
            )

            # Add deployment ID if available
            if event.deployment_id:
                if event.deployment_url:
                    deploy_link = (
                        f'<b>Deployment:</b> <a href="{event.deployment_url}">'
                        f'#{event.deployment_id}</a>'
                    )
                    lines.insert(-2, deploy_link)
                else:
                    lines.insert(-2, f"<b>Deployment:</b> #{event.deployment_id}")

        elif event.event_type == "job":
            status = event.job_status or "unknown"
            status_emoji = self._get_status_emoji(status)
            job_name = self._escape_html(event.job_name or "N/A")
            job_stage = self._escape_html(event.job_stage or "N/A")

            lines.extend(
                [
                    f"<b>Job:</b> {job_name}",
                    f"<b>Stage:</b> {job_stage}",
                    f"<b>Status:</b> {status_emoji} {status.upper()}",
                ]
            )

            if event.pipeline_id:
                lines.append(f"<b>Pipeline:</b> #{event.pipeline_id}")

        elif event.event_type == "feature_flag":
            flag_name = self._escape_html(event.feature_flag_name or "N/A")
            active_status = "✅ Active" if event.feature_flag_active else "❌ Inactive"

            lines.extend(
                [
                    f"<b>Flag:</b> {flag_name}",
                    f"<b>Status:</b> {active_status}",
                ]
            )

            if event.feature_flag_description:
                desc = self._escape_html(self._truncate(event.feature_flag_description, 100))
                lines.append(f"<b>Description:</b> {desc}")

        elif event.event_type == "emoji":
            emoji_name = self._escape_html(event.emoji_name or "")
            action = event.emoji_action or "added"
            target_type = self._escape_html(event.emoji_awardable_type or "item")

            lines.extend(
                [
                    f"<b>Emoji:</b> :{emoji_name}:",
                    f"<b>Action:</b> {action.title()}",
                    f"<b>On:</b> {target_type}",
                ]
            )

        elif event.event_type == "access_token":
            token_name = self._escape_html(event.token_name or "N/A")
            expires_at = event.token_expires_at or "N/A"

            lines.extend(
                [
                    f"<b>Token:</b> {token_name}",
                    f"<b>Expires:</b> {expires_at}",
                    "<b>⚠️ Warning:</b> Token will expire soon!",
                ]
            )

        # Add URL as link if present
        url = self._get_event_url(event)
        if url:
            lines.extend(["", f'<a href="{url}">View Details</a>'])

        return {"text": "\n".join(lines), "parse_mode": "HTML"}

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
