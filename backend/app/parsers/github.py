"""GitHub webhook parser"""

from typing import Dict, Any
from app.parsers.base import BaseParser, ParsedEvent


class GitHubParser(BaseParser):
    """Parser for GitHub webhooks"""

    def can_parse(self, headers: Dict[str, str], payload: Dict[str, Any]) -> bool:
        """Check if this is a GitHub webhook"""
        return "x-github-event" in headers or "repository" in payload

    def parse(self, headers: Dict[str, str], payload: Dict[str, Any]) -> ParsedEvent:
        """Parse GitHub webhook payload"""
        # Normalize headers to lowercase
        headers_lower = {k.lower(): v for k, v in headers.items()}
        event_type = headers_lower.get("x-github-event", "")

        # Route to specific parser based on event type
        if event_type == "push":
            return self._parse_push(payload)
        elif event_type == "pull_request":
            return self._parse_pull_request(payload)
        elif event_type == "workflow_run" or event_type == "check_run":
            return self._parse_workflow(payload)
        elif event_type == "workflow_job":
            return self._parse_workflow_job(payload)
        elif event_type == "issues":
            return self._parse_issue(payload)
        elif (
            event_type == "issue_comment" or event_type == "pull_request_review_comment"
        ):
            return self._parse_comment(payload)
        elif event_type == "create":
            return self._parse_create(payload)
        elif event_type == "delete":
            return self._parse_delete(payload)
        elif event_type == "release":
            return self._parse_release(payload)
        elif event_type == "deployment" or event_type == "deployment_status":
            return self._parse_deployment(payload)
        elif event_type == "fork":
            return self._parse_fork(payload)
        elif event_type == "star":
            return self._parse_star(payload)
        elif event_type == "watch":
            return self._parse_watch(payload)
        elif event_type == "gollum":
            return self._parse_gollum(payload)
        elif event_type == "discussion":
            return self._parse_discussion(payload)
        elif event_type == "discussion_comment":
            return self._parse_discussion_comment(payload)
        elif event_type == "commit_comment":
            return self._parse_commit_comment(payload)
        elif event_type == "code_scanning_alert":
            return self._parse_code_scanning_alert(payload)
        elif event_type == "secret_scanning_alert":
            return self._parse_secret_scanning_alert(payload)
        elif event_type == "dependabot_alert":
            return self._parse_dependabot_alert(payload)
        elif event_type == "branch_protection_rule":
            return self._parse_branch_protection_rule(payload)
        elif event_type == "repository":
            return self._parse_repository(payload)
        elif event_type == "public":
            return self._parse_public(payload)
        elif event_type == "member":
            return self._parse_member(payload)
        elif event_type == "membership":
            return self._parse_membership(payload)
        elif event_type == "project" or event_type == "project_card" or event_type == "project_column":
            return self._parse_project(payload, event_type)
        elif event_type == "projects_v2" or event_type == "projects_v2_item":
            return self._parse_projects_v2(payload, event_type)
        elif event_type == "organization":
            return self._parse_organization(payload)
        elif event_type == "team" or event_type == "team_add":
            return self._parse_team(payload, event_type)
        elif event_type == "sponsorship":
            return self._parse_sponsorship(payload)
        elif event_type == "check_suite":
            return self._parse_check_suite(payload)
        else:
            return self._parse_unknown(payload)

    def _parse_push(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse push event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        ref = payload.get("ref", "").replace("refs/heads/", "")

        return ParsedEvent(
            platform="github",
            event_type="push",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            ref=ref,
            commits=payload.get("commits", []),
            commit_count=len(payload.get("commits", [])),
            raw_data=payload,
        )

    def _parse_pull_request(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse pull request event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        pr = payload.get("pull_request", {})

        return ParsedEvent(
            platform="github",
            event_type="pull_request",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            mr_iid=pr.get("number"),
            mr_title=pr.get("title", ""),
            mr_description=self._truncate(pr.get("body", "")),
            mr_url=pr.get("html_url", ""),
            mr_state=pr.get("state", ""),
            mr_action=payload.get("action", ""),
            source_branch=pr.get("head", {}).get("ref", ""),
            target_branch=pr.get("base", {}).get("ref", ""),
            raw_data=payload,
        )

    def _parse_workflow(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse GitHub Actions workflow event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        workflow = payload.get("workflow_run") or payload.get("check_run", {})

        status = workflow.get("conclusion") or workflow.get("status", "")

        return ParsedEvent(
            platform="github",
            event_type="pipeline",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            ref=workflow.get("head_branch", ""),
            pipeline_id=workflow.get("id"),
            pipeline_status=status,
            pipeline_url=workflow.get("html_url", ""),
            raw_data=payload,
        )

    def _parse_workflow_job(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse GitHub Actions workflow job event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        job = payload.get("workflow_job", {})

        # Map GitHub job status to our standard status
        status = job.get("conclusion") or job.get("status", "")
        if status == "queued":
            status = "pending"

        return ParsedEvent(
            platform="github",
            event_type="job",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            ref=job.get("head_branch", ""),
            job_id=job.get("id"),
            job_name=job.get("name", ""),
            job_status=status,
            pipeline_id=job.get("run_id"),
            pipeline_url=job.get("html_url", ""),
            raw_data=payload,
        )

    def _parse_issue(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse issue event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        issue = payload.get("issue", {})

        return ParsedEvent(
            platform="github",
            event_type="issue",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            issue_iid=issue.get("number"),
            issue_title=issue.get("title", ""),
            issue_description=self._truncate(issue.get("body", "")),
            issue_url=issue.get("html_url", ""),
            issue_state=issue.get("state", ""),
            issue_action=payload.get("action", ""),
            raw_data=payload,
        )

    def _parse_comment(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse comment event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        comment = payload.get("comment", {})

        return ParsedEvent(
            platform="github",
            event_type="comment",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            comment_body=self._truncate(comment.get("body", "")),
            comment_url=comment.get("html_url", ""),
            raw_data=payload,
        )

    def _parse_create(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse create event (branch or tag)"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        ref_type = payload.get("ref_type", "")
        ref = payload.get("ref", "")

        # Determine event type based on what was created
        event_type = "tag_push" if ref_type == "tag" else "branch_create"

        return ParsedEvent(
            platform="github",
            event_type=event_type,
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            ref=ref,
            raw_data=payload,
        )

    def _parse_delete(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse delete event (branch or tag)"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        ref_type = payload.get("ref_type", "")
        ref = payload.get("ref", "")

        # Determine event type based on what was deleted
        event_type = "tag_delete" if ref_type == "tag" else "branch_delete"

        return ParsedEvent(
            platform="github",
            event_type=event_type,
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            ref=ref,
            raw_data=payload,
        )

    def _parse_release(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse release event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        release = payload.get("release", {})

        return ParsedEvent(
            platform="github",
            event_type="release",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            release_tag=release.get("tag_name", ""),
            release_name=release.get("name", ""),
            release_description=self._truncate(release.get("body", "")),
            release_url=release.get("html_url", ""),
            raw_data=payload,
        )

    def _parse_deployment(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse deployment event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        deployment = payload.get("deployment", {})
        deployment_status = payload.get("deployment_status", {})

        # Get status from deployment_status if available, else from deployment
        status = (
            deployment_status.get("state")
            or deployment.get("status")
            or "pending"
        )

        return ParsedEvent(
            platform="github",
            event_type="deployment",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            ref=deployment.get("ref", ""),
            deployment_id=deployment.get("id"),
            deployment_environment=deployment.get("environment", ""),
            deployment_status=status,
            deployment_url=deployment_status.get("target_url")
            or deployment.get("url", ""),
            raw_data=payload,
        )

    def _parse_fork(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse fork event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        forkee = payload.get("forkee", {})

        return ParsedEvent(
            platform="github",
            event_type="fork",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            fork_count=repository.get("forks_count", 0),
            forked_repo_url=forkee.get("html_url", ""),
            raw_data=payload,
        )

    def _parse_star(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse star event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        action = payload.get("action", "")

        return ParsedEvent(
            platform="github",
            event_type="star",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            star_action=action,
            star_count=repository.get("stargazers_count", 0),
            raw_data=payload,
        )

    def _parse_watch(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse watch event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        action = payload.get("action", "")

        return ParsedEvent(
            platform="github",
            event_type="watch",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            watch_action=action,
            raw_data=payload,
        )

    def _parse_gollum(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse gollum (wiki) event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        pages = payload.get("pages", [])

        return ParsedEvent(
            platform="github",
            event_type="wiki",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            wiki_pages=pages,
            raw_data=payload,
        )

    def _parse_discussion(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse discussion event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        discussion = payload.get("discussion", {})

        return ParsedEvent(
            platform="github",
            event_type="discussion",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            discussion_id=discussion.get("number"),
            discussion_title=discussion.get("title", ""),
            discussion_body=self._truncate(discussion.get("body", "")),
            discussion_url=discussion.get("html_url", ""),
            discussion_action=payload.get("action", ""),
            discussion_category=discussion.get("category", {}).get("name", ""),
            raw_data=payload,
        )

    def _parse_discussion_comment(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse discussion comment event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        comment = payload.get("comment", {})
        discussion = payload.get("discussion", {})

        return ParsedEvent(
            platform="github",
            event_type="discussion_comment",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            discussion_id=discussion.get("number"),
            discussion_title=discussion.get("title", ""),
            discussion_url=discussion.get("html_url", ""),
            comment_body=self._truncate(comment.get("body", "")),
            comment_url=comment.get("html_url", ""),
            raw_data=payload,
        )

    def _parse_commit_comment(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse commit comment event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        comment = payload.get("comment", {})

        return ParsedEvent(
            platform="github",
            event_type="commit_comment",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            comment_body=self._truncate(comment.get("body", "")),
            comment_url=comment.get("html_url", ""),
            raw_data=payload,
        )

    def _parse_code_scanning_alert(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse code scanning alert event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        alert = payload.get("alert", {})
        rule = alert.get("rule", {})

        return ParsedEvent(
            platform="github",
            event_type="code_scanning_alert",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            alert_id=alert.get("number"),
            alert_type="code_scanning",
            alert_severity=rule.get("severity", ""),
            alert_state=alert.get("state", ""),
            alert_url=alert.get("html_url", ""),
            alert_description=self._truncate(rule.get("description", "")),
            raw_data=payload,
        )

    def _parse_secret_scanning_alert(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse secret scanning alert event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        alert = payload.get("alert", {})

        return ParsedEvent(
            platform="github",
            event_type="secret_scanning_alert",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            alert_id=alert.get("number"),
            alert_type="secret_scanning",
            alert_state=alert.get("state", ""),
            alert_url=alert.get("html_url", ""),
            alert_description=f"Secret type: {alert.get('secret_type', 'Unknown')}",
            raw_data=payload,
        )

    def _parse_dependabot_alert(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse dependabot alert event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        alert = payload.get("alert", {})
        security_advisory = alert.get("security_advisory", {})
        security_vulnerability = alert.get("security_vulnerability", {})
        package = security_vulnerability.get("package", {})

        return ParsedEvent(
            platform="github",
            event_type="dependabot_alert",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            alert_id=alert.get("number"),
            alert_type="dependabot",
            alert_severity=security_advisory.get("severity", ""),
            alert_state=alert.get("state", ""),
            alert_url=alert.get("html_url", ""),
            alert_description=self._truncate(
                f"{package.get('name', 'Unknown package')}: {security_advisory.get('summary', '')}"
            ),
            raw_data=payload,
        )

    def _parse_branch_protection_rule(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse branch protection rule event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        rule = payload.get("rule", {})

        return ParsedEvent(
            platform="github",
            event_type="branch_protection_rule",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            rule_id=rule.get("id"),
            rule_name=rule.get("name", ""),
            rule_enforcement=payload.get("action", ""),
            raw_data=payload,
        )

    def _parse_repository(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse repository event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        action = payload.get("action", "")

        return ParsedEvent(
            platform="github",
            event_type="repository",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            repo_action=action,
            repo_description=repository.get("description", ""),
            repo_visibility=repository.get("visibility", ""),
            raw_data=payload,
        )

    def _parse_public(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse public event (repository made public)"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})

        return ParsedEvent(
            platform="github",
            event_type="public",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            repo_action="publicized",
            repo_visibility="public",
            raw_data=payload,
        )

    def _parse_member(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse member event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        member = payload.get("member", {})
        action = payload.get("action", "")

        return ParsedEvent(
            platform="github",
            event_type="member",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            member_username=member.get("login", ""),
            member_action=action,
            raw_data=payload,
        )

    def _parse_membership(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse membership event (team membership changes)"""
        sender = payload.get("sender", {})
        member = payload.get("member", {})
        team = payload.get("team", {})
        action = payload.get("action", "")
        org = payload.get("organization", {})

        return ParsedEvent(
            platform="github",
            event_type="membership",
            project=org.get("login", "Organization"),
            project_url=org.get("url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            member_username=member.get("login", ""),
            member_action=action,
            team_name=team.get("name", ""),
            raw_data=payload,
        )

    def _parse_project(self, payload: Dict[str, Any], event_type: str) -> ParsedEvent:
        """Parse project (classic) events"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        project = payload.get("project", {})
        action = payload.get("action", "")

        return ParsedEvent(
            platform="github",
            event_type=event_type,
            project=repository.get("full_name", "") if repository else "Organization",
            project_url=repository.get("html_url", "") if repository else "",
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            project_id=project.get("id"),
            project_name=project.get("name", ""),
            project_action=action,
            raw_data=payload,
        )

    def _parse_projects_v2(self, payload: Dict[str, Any], event_type: str) -> ParsedEvent:
        """Parse projects v2 events"""
        sender = payload.get("sender", {})
        projects_v2 = payload.get("projects_v2", {})
        action = payload.get("action", "")
        org = payload.get("organization", {})

        return ParsedEvent(
            platform="github",
            event_type=event_type,
            project=org.get("login", "Organization") if org else "Projects",
            project_url=org.get("url", "") if org else "",
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            project_id=projects_v2.get("id"),
            project_name=projects_v2.get("title", ""),
            project_action=action,
            raw_data=payload,
        )

    def _parse_organization(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse organization events"""
        sender = payload.get("sender", {})
        organization = payload.get("organization", {})
        action = payload.get("action", "")

        return ParsedEvent(
            platform="github",
            event_type="organization",
            project=organization.get("login", "Organization"),
            project_url=organization.get("url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            repo_action=action,
            raw_data=payload,
        )

    def _parse_team(self, payload: Dict[str, Any], event_type: str) -> ParsedEvent:
        """Parse team events"""
        sender = payload.get("sender", {})
        team = payload.get("team", {})
        action = payload.get("action", "")
        org = payload.get("organization", {})

        return ParsedEvent(
            platform="github",
            event_type=event_type,
            project=org.get("login", "Organization"),
            project_url=org.get("url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            team_name=team.get("name", ""),
            team_action=action,
            raw_data=payload,
        )

    def _parse_sponsorship(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse sponsorship events"""
        sender = payload.get("sender", {})
        sponsorship = payload.get("sponsorship", {})
        sponsor = sponsorship.get("sponsor", {})
        action = payload.get("action", "")

        return ParsedEvent(
            platform="github",
            event_type="sponsorship",
            project="GitHub Sponsors",
            project_url="",
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            sponsor_username=sponsor.get("login", ""),
            sponsor_tier=sponsorship.get("tier", {}).get("name", ""),
            sponsor_action=action,
            raw_data=payload,
        )

    def _parse_check_suite(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse check suite events"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})
        check_suite = payload.get("check_suite", {})

        return ParsedEvent(
            platform="github",
            event_type="check_suite",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            check_suite_id=check_suite.get("id"),
            check_suite_status=check_suite.get("status", ""),
            check_suite_conclusion=check_suite.get("conclusion", ""),
            check_suite_url=check_suite.get("url", ""),
            raw_data=payload,
        )

    def _parse_unknown(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse unknown event type"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})

        return ParsedEvent(
            platform="github",
            event_type="unknown",
            project=repository.get("full_name", "Unknown"),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            raw_data=payload,
        )
