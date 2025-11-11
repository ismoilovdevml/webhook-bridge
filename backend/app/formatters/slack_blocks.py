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
        try:
            emoji = self._get_event_emoji(event.event_type)
        except Exception:
            emoji = "📢"

        try:
            blocks: List[Dict[str, Any]] = []

            # Header block
            blocks.append(
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{emoji} {event.event_type.replace('_', ' ').title()}",
                        "emoji": True,
                    },
                }
            )

            # Main info section
            fields: List[Dict[str, Any]] = [
                {"type": "mrkdwn", "text": f"*Project:*\n{event.project}"},
                {"type": "mrkdwn", "text": f"*Author:*\n{event.author}"},
            ]

            if event.ref:
                fields.append({"type": "mrkdwn", "text": f"*Branch:*\n`{event.ref}`"})

            blocks.append({"type": "section", "fields": fields})

            # Event-specific sections
            if event.event_type == "push" and event.commits:
                commit_lines = [f"*Commits:* {len(event.commits)}"]
                for commit in event.commits[:3]:
                    commit_id = commit.get("id", "")[:8]
                    msg = self._truncate(commit.get("message", ""), 80)
                    commit_lines.append(f"• `{commit_id}` {msg}")
                if len(event.commits) > 3:
                    commit_lines.append(f"• ... and {len(event.commits) - 3} more")

                blocks.append(
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": "\n".join(commit_lines)},
                    }
                )

            elif event.event_type in ["merge_request", "pull_request"]:
                mr_data = event.raw_data
                status = mr_data.get("status", "opened")
                status_emoji = self._get_status_emoji(status)

                mr_fields: List[Dict[str, Any]] = [
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:*\n{status_emoji} {status.title()}",
                    }
                ]

                if mr_data.get("source_branch") and mr_data.get("target_branch"):
                    source = mr_data["source_branch"]
                    target = mr_data["target_branch"]
                    mr_fields.append(
                        {"type": "mrkdwn", "text": f"*Merge:*\n`{source}` → `{target}`"}
                    )

                blocks.append({"type": "section", "fields": mr_fields})

                if mr_data.get("title"):
                    blocks.append(
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Title:*\n{mr_data['title']}",
                            },
                        }
                    )

            elif event.event_type in ["pipeline", "workflow_run"]:
                pipeline_data = event.raw_data
                status = pipeline_data.get("status", "unknown")
                status_emoji = self._get_status_emoji(status)

                pipeline_fields: List[Dict[str, Any]] = [
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:*\n{status_emoji} {status.upper()}",
                    }
                ]

                if pipeline_data.get("duration"):
                    pipeline_fields.append(
                        {
                            "type": "mrkdwn",
                            "text": f"*Duration:*\n{pipeline_data['duration']}s",
                        }
                    )

                blocks.append({"type": "section", "fields": pipeline_fields})

                if pipeline_data.get("stages"):
                    stages_text = ", ".join(pipeline_data["stages"])
                    blocks.append(
                        {
                            "type": "section",
                            "text": {"type": "mrkdwn", "text": f"*Stages:*\n{stages_text}"},
                        }
                    )

            elif event.event_type in ["issue", "issues"]:
                issue_data = event.raw_data
                status = issue_data.get("action", "opened")
                status_emoji = self._get_status_emoji(status)

                blocks.append(
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Action:*\n{status_emoji} {status.title()}",
                            }
                        ],
                    }
                )

                if issue_data.get("title"):
                    blocks.append(
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Title:*\n{issue_data['title']}",
                            },
                        }
                    )

            elif event.event_type in ["comment", "note"]:
                comment_data = event.raw_data
                comment_body = self._truncate(comment_data.get("body", ""), 150)

                noteable_type = comment_data.get("noteable_type", "Unknown")
                comment_text = f"*Comment on:* {noteable_type}\n\n{comment_body}"
                blocks.append(
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": comment_text},
                    }
                )

            elif event.event_type == "job":
                job_status_emoji = self._get_status_emoji(event.job_status)
                status_text = f"{job_status_emoji} {event.job_status.upper()}"
                blocks.append({
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Job:*\n{event.job_name}"},
                        {"type": "mrkdwn", "text": f"*Stage:*\n{event.job_stage}"},
                        {"type": "mrkdwn", "text": f"*Status:*\n{status_text}"},
                        {"type": "mrkdwn", "text": f"*Pipeline:*\n#{event.pipeline_id}"},
                    ],
                })

            elif event.event_type == "wiki":
                wiki_data = event.raw_data.get("object_attributes", {})
                action = wiki_data.get("action", "unknown")
                blocks.append({
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Page:*\n{wiki_data.get('title', 'Unknown')}"},
                        {"type": "mrkdwn", "text": f"*Action:*\n{action.capitalize()}"},
                    ],
                })

            elif event.event_type == "deployment":
                deploy_status_emoji = self._get_status_emoji(event.deployment_status)
                deploy_status_text = (
                    f"{deploy_status_emoji} {event.deployment_status.upper()}"
                )
                deploy_fields: List[Dict[str, Any]] = [
                    {
                        "type": "mrkdwn",
                        "text": f"*Environment:*\n{event.deployment_environment}"
                    },
                    {"type": "mrkdwn", "text": f"*Status:*\n{deploy_status_text}"},
                ]
                if event.ref:
                    deploy_fields.append({"type": "mrkdwn", "text": f"*Ref:*\n`{event.ref}`"})
                blocks.append({"type": "section", "fields": deploy_fields})

            elif event.event_type == "release":
                release_fields: List[Dict[str, Any]] = [
                    {"type": "mrkdwn", "text": f"*Release:*\n{event.release_name}"},
                    {"type": "mrkdwn", "text": f"*Tag:*\n`{event.release_tag}`"},
                ]
                blocks.append({"type": "section", "fields": release_fields})
                if event.release_description:
                    desc = self._truncate(event.release_description, 150)
                    blocks.append({
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"*Description:*\n{desc}"},
                    })

            elif event.event_type == "feature_flag":
                status = "🟢 Enabled" if event.feature_flag_active else "🔴 Disabled"
                flag_fields: List[Dict[str, Any]] = [
                    {"type": "mrkdwn", "text": f"*Flag:*\n{event.feature_flag_name}"},
                    {"type": "mrkdwn", "text": f"*Status:*\n{status}"},
                ]
                blocks.append({"type": "section", "fields": flag_fields})
                if event.feature_flag_description:
                    desc_text = f"*Description:*\n{event.feature_flag_description}"
                    blocks.append({
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": desc_text},
                    })

            elif event.event_type == "milestone":
                action = event.milestone_action or "update"
                milestone_fields: List[Dict[str, Any]] = [
                    {"type": "mrkdwn", "text": f"*Milestone:*\n{event.milestone_title}"},
                    {"type": "mrkdwn", "text": f"*Action:*\n{action.capitalize()}"},
                    {"type": "mrkdwn", "text": f"*State:*\n{event.milestone_state.capitalize()}"},
                ]
                if event.milestone_due_date:
                    due_date_field = {
                        "type": "mrkdwn",
                        "text": f"*Due Date:*\n{event.milestone_due_date}"
                    }
                    milestone_fields.append(due_date_field)
                blocks.append({"type": "section", "fields": milestone_fields})

            elif event.event_type == "vulnerability":
                severity_emoji = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🔵",
                    "unknown": "⚪"
                }.get(event.alert_severity, "⚪")
                severity_text = (
                    f"{severity_emoji} {event.alert_severity.upper()}"
                )
                vuln_fields: List[Dict[str, Any]] = [
                    {"type": "mrkdwn", "text": f"*Severity:*\n{severity_text}"},
                    {"type": "mrkdwn", "text": f"*State:*\n{event.alert_state.capitalize()}"},
                ]
                blocks.append({"type": "section", "fields": vuln_fields})
                if event.alert_description:
                    desc_text = f"*Description:*\n{event.alert_description}"
                    blocks.append({
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": desc_text},
                    })

            elif event.event_type == "emoji":
                action = "added" if event.emoji_action == "award" else "removed"
                blocks.append({
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Emoji:*\n:{event.emoji_name}:"},
                        {"type": "mrkdwn", "text": f"*Action:*\n{action.capitalize()}"},
                        {"type": "mrkdwn", "text": f"*On:*\n{event.emoji_awardable_type}"},
                    ],
                })

            elif event.event_type == "access_token":
                blocks.append({
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Token:*\n{event.token_name}"},
                        {"type": "mrkdwn", "text": f"*⚠️ Expires:*\n{event.token_expires_at}"},
                    ],
                })

            elif event.event_type in ["confidential_issue", "work_item"]:
                issue_data = event.raw_data.get("object_attributes", {})
                action = event.issue_action or "update"
                confidential_badge = "🔒 CONFIDENTIAL" if event.issue_confidential else ""

                work_fields: List[Dict[str, Any]] = [
                    {"type": "mrkdwn", "text": f"*Action:*\n{action.capitalize()}"},
                    {"type": "mrkdwn", "text": f"*State:*\n{event.issue_state.capitalize()}"},
                ]
                if hasattr(event, "work_item_type") and event.work_item_type:
                    type_field = {
                        "type": "mrkdwn",
                        "text": f"*Type:*\n{event.work_item_type}"
                    }
                    work_fields.insert(0, type_field)

                blocks.append({"type": "section", "fields": work_fields})

                if confidential_badge:
                    title_text = f"{confidential_badge}\n*Title:*\n{event.issue_title}"
                else:
                    title_text = f"*Title:*\n{event.issue_title}"
                blocks.append({
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": title_text},
                })

            elif event.event_type == "confidential_comment":
                comment_preview = event.comment_body[:100]
                comment_text = f"🔒 *CONFIDENTIAL COMMENT*\n\n{comment_preview}..."
                blocks.append({
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": comment_text},
                })

            elif event.event_type == "merge_request_approval":
                action = event.mr_action
                if action == "approval":
                    emoji_status = "✅"
                    msg = "Approved"
                elif action == "unapproval":
                    emoji_status = "❌"
                    msg = "Approval Removed"
                elif action == "approved":
                    emoji_status = "✅"
                    msg = "Fully Approved"
                else:
                    emoji_status = "❌"
                    msg = "Approval Revoked"

                merge_text = (
                    f"`{event.source_branch}` → `{event.target_branch}`"
                )
                approval_fields: List[Dict[str, Any]] = [
                    {"type": "mrkdwn", "text": f"*Status:*\n{emoji_status} {msg}"},
                    {"type": "mrkdwn", "text": f"*Merge:*\n{merge_text}"},
                ]
                if event.mr_approvals_required > 0:
                    approved = event.mr_approvals_required - event.mr_approvals_left
                    approvals_text = (
                        f"*Approvals:*\n{approved}/{event.mr_approvals_required}"
                    )
                    approval_fields.append({
                        "type": "mrkdwn",
                        "text": approvals_text
                    })
                blocks.append({"type": "section", "fields": approval_fields})
                blocks.append({
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*MR:*\n{event.mr_title}"},
                })

            elif event.event_type == "repository_update":
                changes = event.repo_changes or []
                blocks.append({
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": "*Repository Updated*"},
                        {"type": "mrkdwn", "text": f"*Changes:*\n{len(changes)} updates"},
                    ],
                })

            # Add button with URL if present
            url = self._get_event_url(event)
            if url:
                blocks.append(
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "View Details",
                                    "emoji": True,
                                },
                                "url": url,
                                "style": "primary",
                            }
                        ],
                    }
                )

            # Fallback text for notifications
            event_title = event.event_type.replace("_", " ").title()
            project = getattr(event, 'project', 'Unknown')
            author = getattr(event, 'author', 'Unknown')
            fallback_text = f"{emoji} {event_title} in {project} by {author}"

            return {"blocks": blocks, "text": fallback_text}
        except Exception as e:
            # Fallback to basic message if formatting fails
            event_title = event.event_type.replace('_', ' ').title()
            project = getattr(event, 'project', 'Unknown')
            author = getattr(event, 'author', 'Unknown')
            error_msg = (
                f"*{emoji} {event_title}*\n\n"
                f"Project: {project}\nAuthor: {author}\n\n"
                f"_Error formatting message: {str(e)}_"
            )
            fallback_blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": error_msg
                    }
                }
            ]
            return {"blocks": fallback_blocks, "text": f"{emoji} {event.event_type} notification"}
