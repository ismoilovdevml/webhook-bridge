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
        try:
            try:
                emoji = self._get_event_emoji(event.event_type)
            except Exception:
                emoji = "📢"

            # Build message parts
            lines = [
                f"### {emoji} {event.event_type.replace('_', ' ').title()}",
                "",
                f"**Project:** {event.project}",
                f"**Author:** {event.author}",
            ]

            # Add branch if present
            if event.ref:
                lines.append(f"**Branch:** `{event.ref}`")

            # Add specific event data
            if event.event_type == "push" and event.commits:
                lines.extend(["", f"**Commits:** {len(event.commits)}"])
                for commit in event.commits[:3]:  # Show first 3 commits
                    msg = self._truncate(commit.get("message", ""), 80)
                    lines.append(f"- `{commit.get('id', '')[:8]}` {msg}")
                if len(event.commits) > 3:
                    lines.append(f"- ... and {len(event.commits) - 3} more")

            elif event.event_type in ["merge_request", "pull_request"]:
                mr_data = event.raw_data
                status = mr_data.get("status", "opened")
                status_emoji = self._get_status_emoji(status)
                lines.extend(
                    [
                        f"**Status:** {status_emoji} {status.title()}",
                        f"**Title:** {mr_data.get('title', 'N/A')}",
                    ]
                )
                if mr_data.get("source_branch") and mr_data.get("target_branch"):
                    lines.append(
                        f"**Merge:** `{mr_data['source_branch']}` → `{mr_data['target_branch']}`"
                    )

            elif event.event_type in ["pipeline", "workflow_run"]:
                pipeline_data = event.raw_data
                status = pipeline_data.get("status", "unknown")
                status_emoji = self._get_status_emoji(status)
                lines.extend(
                    [
                        f"**Status:** {status_emoji} {status.upper()}",
                    ]
                )
                if pipeline_data.get("duration"):
                    duration = pipeline_data["duration"]
                    lines.append(f"**Duration:** {duration}s")

            elif event.event_type in ["issue", "issues"]:
                issue_data = event.raw_data
                status = issue_data.get("action", "opened")
                status_emoji = self._get_status_emoji(status)
                lines.extend(
                    [
                        f"**Action:** {status_emoji} {status.title()}",
                        f"**Title:** {issue_data.get('title', 'N/A')}",
                    ]
                )

            elif event.event_type in ["comment", "note"]:
                comment_data = event.raw_data
                comment_body = self._truncate(comment_data.get("body", ""), 150)
                lines.extend(
                    [
                        f"**Comment on:** {comment_data.get('noteable_type', 'Unknown')}",
                        f"**Comment:** {comment_body}",
                    ]
                )

            elif event.event_type == "job":
                job_status = getattr(event, 'job_status', 'unknown')
                lines.extend([
                    f"**Job:** {getattr(event, 'job_name', 'Unknown')}",
                    f"**Stage:** {getattr(event, 'job_stage', 'Unknown')}",
                    (f"**Status:** {self._get_status_emoji(job_status)} "
                     f"{job_status.upper()}"),
                    f"**Pipeline:** #{getattr(event, 'pipeline_id', 'N/A')}",
                ])

            elif event.event_type == "wiki":
                wiki_data = event.raw_data.get("object_attributes", {})
                action = wiki_data.get("action", "unknown")
                lines.extend([
                    f"**Page:** {wiki_data.get('title', 'Unknown')}",
                    f"**Action:** {action.capitalize()}",
                ])

            elif event.event_type == "deployment":
                lines.extend([
                    f"**Environment:** {event.deployment_environment}",
                    (f"**Status:** {self._get_status_emoji(event.deployment_status)} "
                     f"{event.deployment_status.upper()}"),
                ])
                if event.ref:
                    lines.append(f"**Ref:** `{event.ref}`")

            elif event.event_type == "release":
                lines.extend([
                    f"**Release:** {event.release_name}",
                    f"**Tag:** `{event.release_tag}`",
                ])
                if event.release_description:
                    desc = self._truncate(event.release_description, 150)
                    lines.append(f"**Description:** {desc}")

            elif event.event_type == "feature_flag":
                status = "🟢 Enabled" if event.feature_flag_active else "🔴 Disabled"
                lines.extend([
                    f"**Flag:** {event.feature_flag_name}",
                    f"**Status:** {status}",
                ])
                if event.feature_flag_description:
                    lines.append(f"**Description:** {event.feature_flag_description}")

            elif event.event_type == "milestone":
                action = event.milestone_action or "update"
                lines.extend([
                    f"**Milestone:** {event.milestone_title}",
                    f"**Action:** {action.capitalize()}",
                    f"**State:** {event.milestone_state.capitalize()}",
                ])
                if event.milestone_due_date:
                    lines.append(f"**Due Date:** {event.milestone_due_date}")

            elif event.event_type == "vulnerability":
                severity_emoji = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🔵",
                    "unknown": "⚪"
                }.get(event.alert_severity, "⚪")
                lines.extend([
                    f"**Severity:** {severity_emoji} {event.alert_severity.upper()}",
                    f"**State:** {event.alert_state.capitalize()}",
                ])
                if event.alert_description:
                    lines.append(f"**Description:** {event.alert_description}")

            elif event.event_type == "emoji":
                action = "added" if event.emoji_action == "award" else "removed"
                lines.extend([
                    f"**Emoji:** :{event.emoji_name}:",
                    f"**Action:** {action.capitalize()}",
                    f"**On:** {event.emoji_awardable_type}",
                ])

            elif event.event_type == "access_token":
                lines.extend([
                    f"**Token:** {event.token_name}",
                    f"**⚠️ Expires:** {event.token_expires_at}",
                ])

            elif event.event_type in ["confidential_issue", "work_item"]:
                issue_data = event.raw_data.get("object_attributes", {})
                action = event.issue_action or "update"
                confidential_badge = "🔒 CONFIDENTIAL" if event.issue_confidential else ""
                lines.extend([
                    confidential_badge,
                    f"**Action:** {action.capitalize()}",
                    f"**Title:** {event.issue_title}",
                    f"**State:** {event.issue_state.capitalize()}",
                ])
                if hasattr(event, "work_item_type") and event.work_item_type:
                    lines.insert(2, f"**Type:** {event.work_item_type}")

            elif event.event_type == "confidential_comment":
                lines.extend([
                    "🔒 **CONFIDENTIAL COMMENT**",
                    f"**Comment:** {event.comment_body[:100]}...",
                ])

            elif event.event_type == "merge_request_approval":
                action = event.mr_action
                if action == "approval":
                    emoji = "✅"
                    msg = "Approved"
                elif action == "unapproval":
                    emoji = "❌"
                    msg = "Approval Removed"
                elif action == "approved":
                    emoji = "✅"
                    msg = "Fully Approved"
                else:
                    emoji = "❌"
                    msg = "Approval Revoked"

                lines.extend([
                    f"**Status:** {emoji} {msg}",
                    f"**MR:** {event.mr_title}",
                    f"**Merge:** `{event.source_branch}` → `{event.target_branch}`",
                ])
                if event.mr_approvals_required > 0:
                    approved = event.mr_approvals_required - event.mr_approvals_left
                    lines.append(
                        f"**Approvals:** {approved}/{event.mr_approvals_required}"
                    )

            elif event.event_type == "repository_update":
                changes = event.repo_changes or []
                lines.extend([
                    "**Repository Updated**",
                    f"**Changes:** {len(changes)} updates",
                ])

            # Add URL if present
            url = self._get_event_url(event)
            if url:
                lines.extend(["", f"[View Details]({url})"])

            return {"text": "\n".join(lines)}
        except Exception as e:
            # Fallback to basic message if formatting fails
            fallback_lines = [
                f"### 📢 {event.event_type.replace('_', ' ').title()}",
                "",
                f"**Project:** {getattr(event, 'project', 'Unknown')}",
                f"**Author:** {getattr(event, 'author', 'Unknown')}",
                "",
                f"_Error formatting message: {str(e)}_"
            ]
            return {"text": "\n".join(fallback_lines)}
