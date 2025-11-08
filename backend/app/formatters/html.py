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
        event_name = event.event_type.replace('_', ' ').title()

        # Build message header - include status for pipeline/job events
        if event.event_type in ["pipeline", "workflow_run"]:
            status = event.pipeline_status or "unknown"
            status_emoji = self._get_status_emoji(status)
            header = f"<b>{status_emoji} Pipeline {status.upper()}</b>"
        elif event.event_type == "job":
            status = event.job_status or "unknown"
            status_emoji = self._get_status_emoji(status)
            header = f"<b>{status_emoji} Job {status.upper()}</b>"
        else:
            header = f"<b>{emoji} {event_name}</b>"

        lines = [
            header,
            "",
        ]

        # Project with link
        if event.project_url:
            lines.append(
                f"<b>📦 Project:</b> "
                f'<a href="{event.project_url}">{self._escape_html(event.project)}</a>'
            )
        else:
            lines.append(f"<b>📦 Project:</b> {self._escape_html(event.project)}")

        # Author
        lines.append(f"<b>👤 Author:</b> {self._escape_html(event.author)}")

        # Add branch if present
        if event.ref:
            lines.append(
                f"<b>🌿 Branch:</b> <code>{self._escape_html(event.ref)}</code>"
            )

        # Add specific event data
        if event.event_type == "push" and event.commits:
            lines.extend(["", f"<b>📝 Commits:</b> {len(event.commits)}"])
            for commit in event.commits[:3]:  # Show first 3 commits
                commit_id = commit.get("id", "")[:8]
                commit_url = commit.get("url", "")
                msg = self._escape_html(self._truncate(commit.get("message", ""), 80))
                if commit_url:
                    lines.append(
                        f'  • <a href="{commit_url}"><code>{commit_id}</code></a> {msg}'
                    )
                else:
                    lines.append(f"  • <code>{commit_id}</code> {msg}")
            if len(event.commits) > 3:
                lines.append(f"  • ... and {len(event.commits) - 3} more")

        elif event.event_type in ["merge_request", "pull_request"]:
            status = event.mr_state or event.mr_action or "opened"
            status_emoji = self._get_status_emoji(status)
            title = self._escape_html(event.mr_title or "N/A")

            lines.append("")

            # MR number with link
            if event.mr_iid and event.mr_url:
                lines.append(f'<b>🔗 MR:</b> <a href="{event.mr_url}">!{event.mr_iid}</a>')

            # Status
            lines.append(f"<b>📊 Status:</b> {status_emoji} {status.title()}")

            # Title
            lines.append(f"<b>📋 Title:</b> {title}")

            # Branches
            if event.source_branch and event.target_branch:
                src = self._escape_html(event.source_branch)
                tgt = self._escape_html(event.target_branch)
                lines.append(f"<b>🌿 Merge:</b> <code>{src}</code> → <code>{tgt}</code>")

        elif event.event_type in ["pipeline", "workflow_run"]:
            lines.append("")

            # Pipeline ID with link
            if event.pipeline_id and event.pipeline_url:
                pipeline_link = f'<a href="{event.pipeline_url}">#{event.pipeline_id}</a>'
                lines.append(f"<b>🔗 Pipeline:</b> {pipeline_link}")
            elif event.pipeline_id:
                lines.append(f"<b>🔧 Pipeline:</b> #{event.pipeline_id}")

            # Duration
            if event.pipeline_duration:
                duration_min = event.pipeline_duration // 60
                duration_sec = event.pipeline_duration % 60
                if duration_min > 0:
                    lines.append(f"<b>⏱ Duration:</b> {duration_min}m {duration_sec}s")
                else:
                    lines.append(f"<b>⏱ Duration:</b> {duration_sec}s")

            # Stages
            if event.pipeline_stages:
                lines.append(f"<b>📦 Stages:</b> {', '.join(event.pipeline_stages)}")

        elif event.event_type in ["issue", "issues"]:
            status = event.issue_action or event.issue_state or "opened"
            status_emoji = self._get_status_emoji(status)
            title = self._escape_html(event.issue_title or "N/A")

            lines.append("")

            # Issue number with link
            if event.issue_iid and event.issue_url:
                lines.append(f'<b>🔗 Issue:</b> <a href="{event.issue_url}">#{event.issue_iid}</a>')
            elif event.issue_iid:
                lines.append(f"<b>🐛 Issue:</b> #{event.issue_iid}")

            # Action/Status
            lines.append(f"<b>📊 Action:</b> {status_emoji} {status.title()}")

            # Title
            lines.append(f"<b>📋 Title:</b> {title}")

            # Description if available
            if event.issue_description:
                desc = self._escape_html(self._truncate(event.issue_description, 100))
                lines.append(f"<b>📝 Description:</b> {desc}")

        elif event.event_type in ["comment", "note"]:
            comment_body = self._escape_html(
                self._truncate(event.comment_body or "", 200)
            )
            noteable_type = self._escape_html(
                event.raw_data.get("noteable_type", "Unknown")
            )

            lines.append("")
            lines.append(f"<b>💬 Comment on:</b> {noteable_type}")

            # Comment preview with link
            if event.comment_url:
                lines.append(f"<b>📝 Message:</b> {comment_body}")
                lines.append(f'<b>🔗 Link:</b> <a href="{event.comment_url}">View comment</a>')
            else:
                lines.append(f"<b>📝 Comment:</b> {comment_body}")

        elif event.event_type == "release":
            tag = self._escape_html(event.release_tag or "N/A")
            name = self._escape_html(event.release_name or "N/A")

            lines.append("")

            # Release name with link
            if event.release_url:
                lines.append(f'<b>🚀 Release:</b> <a href="{event.release_url}">{name}</a>')
            else:
                lines.append(f"<b>🚀 Release:</b> {name}")

            # Tag
            lines.append(f"<b>🏷 Tag:</b> <code>{tag}</code>")

            # Description
            if event.release_description:
                desc = self._escape_html(self._truncate(event.release_description, 150))
                lines.append(f"<b>📝 Description:</b> {desc}")

        elif event.event_type == "deployment":
            status = event.deployment_status or "unknown"
            status_emoji = self._get_status_emoji(status)
            environment = self._escape_html(event.deployment_environment or "N/A")

            lines.append("")

            # Deployment ID with link
            if event.deployment_id and event.deployment_url:
                deploy_link = f'<a href="{event.deployment_url}">#{event.deployment_id}</a>'
                lines.append(f"<b>🔗 Deployment:</b> {deploy_link}")
            elif event.deployment_id:
                lines.append(f"<b>🚢 Deployment:</b> #{event.deployment_id}")

            # Environment
            lines.append(f"<b>🌍 Environment:</b> <code>{environment}</code>")

            # Status
            lines.append(f"<b>📊 Status:</b> {status_emoji} <b>{status.upper()}</b>")

        elif event.event_type == "job":
            job_name = self._escape_html(event.job_name or "N/A")
            job_stage = self._escape_html(event.job_stage or "N/A")

            lines.append("")
            lines.extend(
                [
                    f"<b>⚙️ Job:</b> <code>{job_name}</code>",
                    f"<b>📦 Stage:</b> {job_stage}",
                ]
            )

            if event.pipeline_id and event.pipeline_url:
                lines.append(
                    f'<b>🔗 Pipeline:</b> <a href="{event.pipeline_url}">#{event.pipeline_id}</a>'
                )
            elif event.pipeline_id:
                lines.append(f"<b>🔧 Pipeline:</b> #{event.pipeline_id}")

        elif event.event_type == "wiki":
            lines.append("")
            lines.append("<b>📝 Wiki Page Updated</b>")
            if event.ref:
                lines.append(f"<b>📄 Page:</b> {self._escape_html(event.ref)}")

        elif event.event_type == "feature_flag":
            flag_name = self._escape_html(event.feature_flag_name or "N/A")
            active_status = "✅ Active" if event.feature_flag_active else "❌ Inactive"

            lines.append("")
            lines.extend(
                [
                    f"<b>🚩 Flag:</b> <code>{flag_name}</code>",
                    f"<b>📊 Status:</b> {active_status}",
                ]
            )

            if event.feature_flag_description:
                desc = self._escape_html(self._truncate(event.feature_flag_description, 100))
                lines.append(f"<b>📝 Description:</b> {desc}")

        elif event.event_type == "emoji":
            emoji_name = self._escape_html(event.emoji_name or "")
            action = event.emoji_action or "added"
            target_type = self._escape_html(event.emoji_awardable_type or "item")
            action_emoji = "➕" if action == "added" else "➖"

            lines.append("")
            lines.extend(
                [
                    f"<b>😀 Emoji:</b> :{emoji_name}:",
                    f"<b>🎯 Action:</b> {action_emoji} {action.title()}",
                    f"<b>📍 On:</b> {target_type}",
                ]
            )

        elif event.event_type == "access_token":
            token_name = self._escape_html(event.token_name or "N/A")
            expires_at = event.token_expires_at or "N/A"

            lines.append("")
            lines.extend(
                [
                    f"<b>🔑 Token:</b> <code>{token_name}</code>",
                    f"<b>📅 Expires:</b> {expires_at}",
                    "",
                    "<b>⚠️ Warning:</b> Token will expire soon!",
                ]
            )

        # Add footer with "View Details" link
        url = self._get_event_url(event)
        if url:
            lines.extend(
                [
                    "",
                    "─────────────────",
                    f'<a href="{url}">🔗 View Details</a>',
                ]
            )

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
