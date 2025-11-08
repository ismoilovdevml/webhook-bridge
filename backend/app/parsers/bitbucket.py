"""Bitbucket webhook parser"""

from typing import Dict, Any
from app.parsers.base import BaseParser, ParsedEvent


class BitbucketParser(BaseParser):
    """Parser for Bitbucket webhooks"""

    def can_parse(self, headers: Dict[str, str], payload: Dict[str, Any]) -> bool:
        """Check if this is a Bitbucket webhook"""
        return (
            "x-event-key" in headers
            or "repository" in payload
            and "uuid" in payload.get("repository", {})
        )

    def parse(self, headers: Dict[str, str], payload: Dict[str, Any]) -> ParsedEvent:
        """Parse Bitbucket webhook payload"""
        # Normalize headers to lowercase
        headers_lower = {k.lower(): v for k, v in headers.items()}
        event_key = headers_lower.get("x-event-key", "")

        # Route to specific parser based on event type
        if "push" in event_key:
            return self._parse_push(payload)
        elif "pullrequest" in event_key:
            return self._parse_pull_request(payload, event_key)
        elif "issue" in event_key:
            return self._parse_issue(payload, event_key)
        elif "pipeline" in event_key or "build_status" in event_key:
            return self._parse_pipeline(payload)
        elif event_key == "repo:fork":
            return self._parse_fork(payload)
        elif event_key == "repo:updated":
            return self._parse_repo_updated(payload)
        elif event_key == "repo:transfer":
            return self._parse_repo_transfer(payload)
        elif event_key == "repo:deleted":
            return self._parse_repo_deleted(payload)
        elif event_key == "repo:commit_comment_created":
            return self._parse_commit_comment(payload)
        else:
            return self._parse_unknown(payload)

    def _parse_push(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse push event"""
        repository = payload.get("repository", {})
        actor = payload.get("actor", {})
        changes = payload.get("push", {}).get("changes", [])

        # Get first change for basic info
        first_change = changes[0] if changes else {}
        ref = (
            first_change.get("new", {}).get("name", "")
            if first_change.get("new")
            else ""
        )

        commits = []
        for change in changes:
            if change.get("commits"):
                commits.extend(change["commits"])

        return ParsedEvent(
            platform="bitbucket",
            event_type="push",
            project=repository.get("full_name", ""),
            project_url=repository.get("links", {}).get("html", {}).get("href", ""),
            author=actor.get("display_name", "Unknown"),
            author_username=actor.get("username", ""),
            author_avatar=actor.get("links", {}).get("avatar", {}).get("href", None),
            ref=ref,
            commits=commits,
            commit_count=len(commits),
            raw_data=payload,
        )

    def _parse_pull_request(
        self, payload: Dict[str, Any], event_key: str
    ) -> ParsedEvent:
        """Parse pull request event"""
        repository = payload.get("repository", {})
        actor = payload.get("actor", {})
        pr = payload.get("pullrequest", {})

        # Determine action from event key
        action = "opened"
        if "updated" in event_key:
            action = "updated"
        elif "approved" in event_key:
            action = "approved"
        elif "unapproved" in event_key:
            action = "unapproved"
        elif "merged" in event_key or "fulfilled" in event_key:
            action = "merged"
        elif "declined" in event_key or "rejected" in event_key:
            action = "closed"
        elif "changes_request_created" in event_key:
            action = "changes_requested"
        elif "changes_request_removed" in event_key:
            action = "changes_request_removed"
        elif "comment_created" in event_key:
            action = "comment_created"
        elif "comment_updated" in event_key:
            action = "comment_updated"
        elif "comment_deleted" in event_key:
            action = "comment_deleted"
        elif "comment_resolved" in event_key:
            action = "comment_resolved"
        elif "comment_reopened" in event_key:
            action = "comment_reopened"

        return ParsedEvent(
            platform="bitbucket",
            event_type="pull_request",
            project=repository.get("full_name", ""),
            project_url=repository.get("links", {}).get("html", {}).get("href", ""),
            author=actor.get("display_name", "Unknown"),
            author_username=actor.get("username", ""),
            author_avatar=actor.get("links", {}).get("avatar", {}).get("href", None),
            mr_iid=pr.get("id"),
            mr_title=pr.get("title", ""),
            mr_description=self._truncate(pr.get("description", "")),
            mr_url=pr.get("links", {}).get("html", {}).get("href", ""),
            mr_state=pr.get("state", ""),
            mr_action=action,
            source_branch=pr.get("source", {}).get("branch", {}).get("name", ""),
            target_branch=pr.get("destination", {}).get("branch", {}).get("name", ""),
            raw_data=payload,
        )

    def _parse_issue(self, payload: Dict[str, Any], event_key: str) -> ParsedEvent:
        """Parse issue event"""
        repository = payload.get("repository", {})
        actor = payload.get("actor", {})
        issue = payload.get("issue", {})

        # Determine action from event key
        action = "opened"
        if "updated" in event_key:
            action = "updated"
        elif "comment" in event_key:
            action = "commented"

        return ParsedEvent(
            platform="bitbucket",
            event_type="issue",
            project=repository.get("full_name", ""),
            project_url=repository.get("links", {}).get("html", {}).get("href", ""),
            author=actor.get("display_name", "Unknown"),
            author_username=actor.get("username", ""),
            author_avatar=actor.get("links", {}).get("avatar", {}).get("href", None),
            issue_iid=issue.get("id"),
            issue_title=issue.get("title", ""),
            issue_description=self._truncate(issue.get("content", {}).get("raw", "")),
            issue_url=issue.get("links", {}).get("html", {}).get("href", ""),
            issue_state=issue.get("state", ""),
            issue_action=action,
            raw_data=payload,
        )

    def _parse_pipeline(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse pipeline/build status event"""
        repository = payload.get("repository", {})
        actor = payload.get("actor", {})

        # Bitbucket Pipelines can send either 'pipeline_completed' or 'build_status' events
        pipeline = payload.get("pipeline", {})
        build_status = payload.get("build_status", {})

        # Use pipeline data if available, otherwise build_status
        if pipeline:
            pipeline_id = pipeline.get("build_number")
            status = pipeline.get("state", {}).get("name", "").lower()
            ref = pipeline.get("target", {}).get("ref_name", "")
            duration = pipeline.get("duration_in_seconds")
            url = pipeline.get("url", "")
        else:
            pipeline_id = build_status.get("key")
            status = build_status.get("state", "").lower()
            ref = build_status.get("refname", "")
            duration = None
            url = build_status.get("url", "")

        # Normalize status names
        if status in ["successful", "success"]:
            status = "success"
        elif status in ["failed", "failure"]:
            status = "failed"
        elif status in ["stopped", "stopped"]:
            status = "canceled"
        elif status in ["pending", "in_progress"]:
            status = "running"

        return ParsedEvent(
            platform="bitbucket",
            event_type="pipeline",
            project=repository.get("full_name", ""),
            project_url=repository.get("links", {}).get("html", {}).get("href", ""),
            author=actor.get("display_name", "Unknown"),
            author_username=actor.get("username", ""),
            author_avatar=actor.get("links", {}).get("avatar", {}).get("href", None),
            ref=ref,
            pipeline_id=pipeline_id,
            pipeline_status=status,
            pipeline_url=url,
            pipeline_duration=duration,
            raw_data=payload,
        )

    def _parse_fork(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse fork event"""
        repository = payload.get("repository", {})
        actor = payload.get("actor", {})
        fork = payload.get("fork", {})

        return ParsedEvent(
            platform="bitbucket",
            event_type="fork",
            project=repository.get("full_name", ""),
            project_url=repository.get("links", {}).get("html", {}).get("href", ""),
            author=actor.get("display_name", "Unknown"),
            author_username=actor.get("username", ""),
            author_avatar=actor.get("links", {}).get("avatar", {}).get("href", None),
            forked_repo_url=fork.get("links", {}).get("html", {}).get("href", ""),
            raw_data=payload,
        )

    def _parse_repo_updated(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse repository updated event"""
        repository = payload.get("repository", {})
        actor = payload.get("actor", {})
        changes = payload.get("changes", {})

        return ParsedEvent(
            platform="bitbucket",
            event_type="repository",
            project=repository.get("full_name", ""),
            project_url=repository.get("links", {}).get("html", {}).get("href", ""),
            author=actor.get("display_name", "Unknown"),
            author_username=actor.get("username", ""),
            author_avatar=actor.get("links", {}).get("avatar", {}).get("href", None),
            repo_action="updated",
            repo_description=repository.get("description", ""),
            raw_data=payload,
        )

    def _parse_repo_transfer(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse repository transfer event"""
        repository = payload.get("repository", {})
        actor = payload.get("actor", {})
        previous_workspace = payload.get("previous_workspace", {})

        return ParsedEvent(
            platform="bitbucket",
            event_type="repository",
            project=repository.get("full_name", ""),
            project_url=repository.get("links", {}).get("html", {}).get("href", ""),
            author=actor.get("display_name", "Unknown"),
            author_username=actor.get("username", ""),
            author_avatar=actor.get("links", {}).get("avatar", {}).get("href", None),
            repo_action="transferred",
            raw_data=payload,
        )

    def _parse_repo_deleted(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse repository deleted event"""
        repository = payload.get("repository", {})
        actor = payload.get("actor", {})

        return ParsedEvent(
            platform="bitbucket",
            event_type="repository",
            project=repository.get("full_name", ""),
            project_url=repository.get("links", {}).get("html", {}).get("href", ""),
            author=actor.get("display_name", "Unknown"),
            author_username=actor.get("username", ""),
            author_avatar=actor.get("links", {}).get("avatar", {}).get("href", None),
            repo_action="deleted",
            raw_data=payload,
        )

    def _parse_commit_comment(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse commit comment created event"""
        repository = payload.get("repository", {})
        actor = payload.get("actor", {})
        comment = payload.get("comment", {})
        commit = payload.get("commit", {})

        return ParsedEvent(
            platform="bitbucket",
            event_type="commit_comment",
            project=repository.get("full_name", ""),
            project_url=repository.get("links", {}).get("html", {}).get("href", ""),
            author=actor.get("display_name", "Unknown"),
            author_username=actor.get("username", ""),
            author_avatar=actor.get("links", {}).get("avatar", {}).get("href", None),
            comment_body=self._truncate(
                comment.get("content", {}).get("raw", ""), 200
            ),
            comment_url=comment.get("links", {}).get("html", {}).get("href", ""),
            raw_data=payload,
        )

    def _parse_unknown(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse unknown event type"""
        repository = payload.get("repository", {})
        actor = payload.get("actor", {})

        return ParsedEvent(
            platform="bitbucket",
            event_type="unknown",
            project=repository.get("full_name", "Unknown"),
            project_url=repository.get("links", {}).get("html", {}).get("href", ""),
            author=actor.get("display_name", "Unknown"),
            author_username=actor.get("username", ""),
            author_avatar=actor.get("links", {}).get("avatar", {}).get("href", None),
            raw_data=payload,
        )
