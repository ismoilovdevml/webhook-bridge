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
        elif event_type == "issues":
            return self._parse_issue(payload)
        elif event_type == "issue_comment" or event_type == "pull_request_review_comment":
            return self._parse_comment(payload)
        elif event_type == "create" and payload.get("ref_type") == "tag":
            return self._parse_tag(payload)
        elif event_type == "release":
            return self._parse_release(payload)
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

    def _parse_tag(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse tag creation event"""
        repository = payload.get("repository", {})
        sender = payload.get("sender", {})

        return ParsedEvent(
            platform="github",
            event_type="tag_push",
            project=repository.get("full_name", ""),
            project_url=repository.get("html_url", ""),
            author=sender.get("login", "Unknown"),
            author_username=sender.get("login", ""),
            author_avatar=sender.get("avatar_url", None),
            ref=payload.get("ref", ""),
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
            ref=release.get("tag_name", ""),
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
