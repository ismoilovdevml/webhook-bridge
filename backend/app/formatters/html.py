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
        try:
            emoji = self._get_event_emoji(event.event_type)
        except Exception:
            emoji = "📢"

        try:
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
                    lines.append(
                        f'<b>🔗 Issue:</b> <a href="{event.issue_url}">'
                        f'#{event.issue_iid}</a>'
                    )
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
                        f'<b>🔗 Pipeline:</b> '
                        f'<a href="{event.pipeline_url}">#{event.pipeline_id}</a>'
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

            elif event.event_type == "fork":
                lines.append("")
                lines.append(f"<b>🍴 Fork Count:</b> {event.fork_count or 'N/A'}")
                if event.forked_repo_url:
                    forked_link = f'<a href="{event.forked_repo_url}">View fork</a>'
                    lines.append(f"<b>🔗 Forked Repo:</b> {forked_link}")

            elif event.event_type == "star":
                action = event.star_action or "starred"
                action_emoji = "⭐" if action == "created" else "✖️"
                lines.append("")
                lines.append(f"<b>{action_emoji} Action:</b> {action.title()}")
                lines.append(f"<b>⭐ Star Count:</b> {event.star_count or 'N/A'}")

            elif event.event_type == "watch":
                lines.append("")
                lines.append("<b>👀 Action:</b> Started watching")

            elif event.event_type == "discussion":
                action = event.discussion_action or "opened"
                action_emoji = self._get_status_emoji(action)
                title = self._escape_html(event.discussion_title or "N/A")
                category = self._escape_html(event.discussion_category or "General")

                lines.append("")
                if event.discussion_id and event.discussion_url:
                    disc_link = (
                        f'<a href="{event.discussion_url}">#{event.discussion_id}</a>'
                    )
                    lines.append(f"<b>🔗 Discussion:</b> {disc_link}")
                lines.append(f"<b>📊 Action:</b> {action_emoji} {action.title()}")
                lines.append(f"<b>📋 Title:</b> {title}")
                lines.append(f"<b>📂 Category:</b> {category}")
                if event.discussion_body:
                    desc = self._escape_html(self._truncate(event.discussion_body, 100))
                    lines.append(f"<b>📝 Description:</b> {desc}")

            elif event.event_type == "discussion_comment":
                title = self._escape_html(event.discussion_title or "N/A")
                comment_body = self._escape_html(
                    self._truncate(event.comment_body or "", 200)
                )

                lines.append("")
                if event.discussion_id and event.discussion_url:
                    disc_title = f"#{event.discussion_id} - {title}"
                    disc_link = f'<a href="{event.discussion_url}">{disc_title}</a>'
                    lines.append(f"<b>💬 On Discussion:</b> {disc_link}")
                lines.append(f"<b>📝 Comment:</b> {comment_body}")

            elif event.event_type == "commit_comment":
                comment_body = self._escape_html(
                    self._truncate(event.comment_body or "", 200)
                )
                lines.append("")
                lines.append("<b>💬 Comment on Commit</b>")
                lines.append(f"<b>📝 Message:</b> {comment_body}")

            elif event.event_type == "code_scanning_alert":
                severity = event.alert_severity or "unknown"
                if severity in ["critical", "high"]:
                    severity_emoji = "🔴"
                elif severity == "medium":
                    severity_emoji = "🟡"
                else:
                    severity_emoji = "🟢"
                state = event.alert_state or "open"

                lines.append("")
                if event.alert_id and event.alert_url:
                    alert_link = f'<a href="{event.alert_url}">#{event.alert_id}</a>'
                    lines.append(f"<b>🔒 Alert:</b> {alert_link}")
                lines.append(f"<b>{severity_emoji} Severity:</b> {severity.upper()}")
                lines.append(f"<b>📊 State:</b> {state.title()}")
                if event.alert_description:
                    desc = self._escape_html(event.alert_description)
                    lines.append(f"<b>📝 Description:</b> {desc}")

            elif event.event_type == "secret_scanning_alert":
                state = event.alert_state or "open"

                lines.append("")
                if event.alert_id and event.alert_url:
                    alert_link = f'<a href="{event.alert_url}">#{event.alert_id}</a>'
                    lines.append(f"<b>🔐 Alert:</b> {alert_link}")
                lines.append(f"<b>📊 State:</b> {state.title()}")
                if event.alert_description:
                    desc = self._escape_html(event.alert_description)
                    lines.append(f"<b>📝 Details:</b> {desc}")

            elif event.event_type == "dependabot_alert":
                severity = event.alert_severity or "unknown"
                if severity in ["critical", "high"]:
                    severity_emoji = "🔴"
                elif severity == "medium":
                    severity_emoji = "🟡"
                else:
                    severity_emoji = "🟢"
                state = event.alert_state or "open"

                lines.append("")
                if event.alert_id and event.alert_url:
                    alert_link = f'<a href="{event.alert_url}">#{event.alert_id}</a>'
                    lines.append(f"<b>🤖 Alert:</b> {alert_link}")
                lines.append(f"<b>{severity_emoji} Severity:</b> {severity.upper()}")
                lines.append(f"<b>📊 State:</b> {state.title()}")
                if event.alert_description:
                    desc = self._escape_html(event.alert_description)
                    lines.append(f"<b>📦 Details:</b> {desc}")

            elif event.event_type == "branch_protection_rule":
                rule_name = self._escape_html(event.rule_name or "N/A")
                action = event.rule_enforcement or "updated"

                lines.append("")
                lines.append(f"<b>🛡️ Rule:</b> <code>{rule_name}</code>")
                lines.append(f"<b>📊 Action:</b> {action.title()}")

            elif event.event_type == "repository":
                action = event.repo_action or "updated"
                visibility = event.repo_visibility or "private"

                lines.append("")
                lines.append(f"<b>📦 Action:</b> {action.title()}")
                lines.append(f"<b>👁️ Visibility:</b> {visibility.title()}")
                if event.repo_description:
                    desc = self._escape_html(event.repo_description)
                    lines.append(f"<b>📝 Description:</b> {desc}")

            elif event.event_type == "public":
                lines.append("")
                lines.append("<b>🌍 Repository is now PUBLIC</b>")
                lines.append("<b>👁️ Visibility:</b> Public")

            elif event.event_type == "member":
                member = self._escape_html(event.member_username or "Unknown")
                action = event.member_action or "added"
                action_emoji = "➕" if action == "added" else "➖"

                lines.append("")
                lines.append(f"<b>👥 Member:</b> {member}")
                lines.append(f"<b>{action_emoji} Action:</b> {action.title()}")

            elif event.event_type == "membership":
                member = self._escape_html(event.member_username or "Unknown")
                team = self._escape_html(event.team_name or "Unknown")
                action = event.member_action or "added"
                action_emoji = "➕" if action == "added" else "➖"

                lines.append("")
                lines.append(f"<b>👥 Member:</b> {member}")
                lines.append(f"<b>👨‍👩‍👧‍👦 Team:</b> {team}")
                lines.append(f"<b>{action_emoji} Action:</b> {action.title()}")

            elif event.event_type in [
                "project", "project_card", "project_column",
                "projects_v2", "projects_v2_item"
            ]:
                project_name = self._escape_html(event.project_name or "N/A")
                action = event.project_action or "updated"

                lines.append("")
                lines.append(f"<b>📋 Project:</b> {project_name}")
                lines.append(f"<b>📊 Action:</b> {action.title()}")

            elif event.event_type == "organization":
                action = event.repo_action or "updated"
                lines.append("")
                lines.append(f"<b>🏢 Action:</b> {action.title()}")

            elif event.event_type in ["team", "team_add"]:
                team = self._escape_html(event.team_name or "Unknown")
                action = event.team_action or "updated"

                lines.append("")
                lines.append(f"<b>👨‍👩‍👧‍👦 Team:</b> {team}")
                lines.append(f"<b>📊 Action:</b> {action.title()}")

            elif event.event_type == "sponsorship":
                sponsor = self._escape_html(event.sponsor_username or "Unknown")
                tier = self._escape_html(event.sponsor_tier or "N/A")
                action = event.sponsor_action or "created"
                action_emoji = "💖" if action == "created" else "❌"

                lines.append("")
                lines.append(f"<b>💝 Sponsor:</b> {sponsor}")
                lines.append(f"<b>🎯 Tier:</b> {tier}")
                lines.append(f"<b>{action_emoji} Action:</b> {action.title()}")

            elif event.event_type == "check_suite":
                status = event.check_suite_status or "unknown"
                conclusion = event.check_suite_conclusion or "pending"
                status_emoji = self._get_status_emoji(conclusion or status)

                lines.append("")
                if event.check_suite_id:
                    lines.append(f"<b>✅ Check Suite:</b> #{event.check_suite_id}")
                lines.append(f"<b>📊 Status:</b> {status_emoji} {status.title()}")
                if conclusion:
                    lines.append(f"<b>🎯 Conclusion:</b> {conclusion.title()}")

            elif event.event_type == "branch_create":
                branch = self._escape_html(event.ref or "N/A")
                lines.append("")
                lines.append(f"<b>🌿 Branch Created:</b> <code>{branch}</code>")

            elif event.event_type == "branch_delete":
                branch = self._escape_html(event.ref or "N/A")
                lines.append("")
                lines.append(f"<b>🗑️ Branch Deleted:</b> <code>{branch}</code>")

            elif event.event_type == "tag_delete":
                tag = self._escape_html(event.ref or "N/A")
                lines.append("")
                lines.append(f"<b>🗑️ Tag Deleted:</b> <code>{tag}</code>")

            elif event.event_type == "milestone":
                title = self._escape_html(event.milestone_title or "N/A")
                state = event.milestone_state or "active"
                action = event.milestone_action or "created"
                state_emoji = self._get_status_emoji(state)

                lines.append("")
                if event.milestone_id:
                    lines.append(f"<b>🎯 Milestone:</b> {title}")
                lines.append(f"<b>📊 Action:</b> {action.title()}")
                lines.append(f"<b>{state_emoji} State:</b> {state.title()}")
                if event.milestone_due_date:
                    lines.append(f"<b>📅 Due Date:</b> {event.milestone_due_date}")
                if event.milestone_description:
                    desc = self._escape_html(event.milestone_description)
                    lines.append(f"<b>📝 Description:</b> {desc}")

            elif event.event_type == "vulnerability":
                severity = event.alert_severity or "unknown"
                if severity in ["critical", "high"]:
                    severity_emoji = "🔴"
                elif severity == "medium":
                    severity_emoji = "🟡"
                else:
                    severity_emoji = "🟢"
                state = event.alert_state or "open"

                lines.append("")
                if event.alert_id and event.alert_url:
                    vuln_link = f'<a href="{event.alert_url}">#{event.alert_id}</a>'
                    lines.append(f"<b>🛡️ Vulnerability:</b> {vuln_link}")
                lines.append(f"<b>{severity_emoji} Severity:</b> {severity.upper()}")
                lines.append(f"<b>📊 State:</b> {state.title()}")
                if event.alert_description:
                    desc = self._escape_html(event.alert_description)
                    lines.append(f"<b>📝 Description:</b> {desc}")

            elif event.event_type == "confidential_issue":
                issue_title = self._escape_html(event.issue_title or "N/A")
                issue_iid = event.issue_iid or "N/A"
                state = event.issue_state or "opened"
                action = event.issue_action or "update"
                state_emoji = self._get_status_emoji(state)

                lines.append("")
                lines.append("<b>🔒 CONFIDENTIAL ISSUE</b>")
                if event.issue_url:
                    issue_link = f'<a href="{event.issue_url}">#{issue_iid}</a>'
                    lines.append(f"<b>📋 Issue:</b> {issue_link}")
                else:
                    lines.append(f"<b>📋 Issue:</b> #{issue_iid}")
                lines.append(f"<b>📝 Title:</b> {issue_title}")
                lines.append(f"<b>📊 Action:</b> {action.title()}")
                lines.append(f"<b>{state_emoji} State:</b> {state.title()}")
                if event.issue_description:
                    desc = self._truncate(self._escape_html(event.issue_description), 200)
                    lines.append(f"<b>💬 Description:</b> {desc}")
                if getattr(event, 'issue_service_desk', False):
                    lines.append("<b>🎫 Type:</b> Service Desk")

            elif event.event_type == "work_item":
                work_title = self._escape_html(event.issue_title or "N/A")
                work_iid = event.issue_iid or "N/A"
                work_type = getattr(event, 'work_item_type', 'WorkItem')
                state = event.issue_state or "opened"
                action = event.issue_action or "update"
                state_emoji = self._get_status_emoji(state)
                is_confidential = getattr(event, 'issue_confidential', False)

                lines.append("")
                if is_confidential:
                    lines.append("<b>🔒 CONFIDENTIAL WORK ITEM</b>")
                lines.append(f"<b>📦 Type:</b> {work_type}")
                if event.issue_url:
                    work_link = f'<a href="{event.issue_url}">#{work_iid}</a>'
                    lines.append(f"<b>🔖 Work Item:</b> {work_link}")
                else:
                    lines.append(f"<b>🔖 Work Item:</b> #{work_iid}")
                lines.append(f"<b>📝 Title:</b> {work_title}")
                lines.append(f"<b>📊 Action:</b> {action.title()}")
                lines.append(f"<b>{state_emoji} State:</b> {state.title()}")
                if event.issue_description:
                    desc = self._truncate(self._escape_html(event.issue_description), 200)
                    lines.append(f"<b>💬 Description:</b> {desc}")

            elif event.event_type == "confidential_comment":
                comment_body = self._escape_html(event.comment_body or "N/A")
                comment_preview = self._truncate(comment_body, 150)

                lines.append("")
                lines.append("<b>🔒 CONFIDENTIAL COMMENT</b>")
                lines.append(f"<b>💬 Comment:</b> {comment_preview}")
                if event.comment_url:
                    lines.append(f'<a href="{event.comment_url}">View Comment</a>')

            elif event.event_type == "merge_request_approval":
                mr_title = self._escape_html(event.mr_title or "N/A")
                mr_iid = event.mr_iid or "N/A"
                action = event.mr_action or "approval"
                source = self._escape_html(event.source_branch or "N/A")
                target = self._escape_html(event.target_branch or "N/A")

                if action == "approval":
                    approval_emoji = "✅"
                    approval_msg = "Approved"
                elif action == "unapproval":
                    approval_emoji = "❌"
                    approval_msg = "Approval Removed"
                elif action == "approved":
                    approval_emoji = "✅"
                    approval_msg = "Fully Approved"
                else:
                    approval_emoji = "❌"
                    approval_msg = "Approval Revoked"

                lines.append("")
                if event.mr_url:
                    mr_link = f'<a href="{event.mr_url}">!{mr_iid}</a>'
                    lines.append(f"<b>🔀 Merge Request:</b> {mr_link}")
                else:
                    lines.append(f"<b>🔀 Merge Request:</b> !{mr_iid}")
                lines.append(f"<b>📝 Title:</b> {mr_title}")
                lines.append(f"<b>{approval_emoji} Status:</b> {approval_msg}")
                lines.append(f"<b>🔄 Merge:</b> <code>{source}</code> → <code>{target}</code>")

                approvals_required = getattr(event, 'mr_approvals_required', 0)
                approvals_left = getattr(event, 'mr_approvals_left', 0)
                if approvals_required > 0:
                    approved_count = approvals_required - approvals_left
                    lines.append(f"<b>✅ Approvals:</b> {approved_count}/{approvals_required}")

            elif event.event_type == "repository_update":
                changes = getattr(event, 'repo_changes', [])
                change_count = len(changes) if isinstance(changes, list) else 0

                lines.append("")
                lines.append("<b>🔄 Repository Updated</b>")
                lines.append(f"<b>📊 Changes:</b> {change_count} updates")
                if change_count > 0 and isinstance(changes, list):
                    for i, change in enumerate(changes[:5]):
                        if isinstance(change, dict):
                            change_type = change.get('type', 'update')
                            lines.append(f"  • {change_type}")
                    if change_count > 5:
                        lines.append(f"  • ... and {change_count - 5} more")

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
        except Exception as e:
            # Fallback to basic message if formatting fails
            project = self._escape_html(getattr(event, 'project', 'Unknown'))
            author = self._escape_html(getattr(event, 'author', 'Unknown'))
            event_name = event.event_type.replace('_', ' ').title()

            fallback = f"""<b>{emoji} {event_name}</b>

<b>📁 Project:</b> {project}
<b>👤 Author:</b> {author}

<i>⚠️ Error formatting message: {self._escape_html(str(e))}</i>"""
            return {"text": fallback, "parse_mode": "HTML"}

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
