"""GitLab webhook parser"""
from typing import Dict, Any
from app.parsers.base import BaseParser, ParsedEvent


class GitLabParser(BaseParser):
    """Parser for GitLab webhooks"""

    def can_parse(self, headers: Dict[str, str], payload: Dict[str, Any]) -> bool:
        """Check if this is a GitLab webhook"""
        return "x-gitlab-event" in headers or "object_kind" in payload

    def parse(self, headers: Dict[str, str], payload: Dict[str, Any]) -> ParsedEvent:
        """Parse GitLab webhook payload"""
        object_kind = payload.get("object_kind", "")
        event_name = payload.get("event_name", "")

        # Route to specific parser based on event type
        if object_kind == "push" or event_name == "push":
            return self._parse_push(payload)
        elif object_kind == "merge_request":
            return self._parse_merge_request(payload)
        elif object_kind == "pipeline":
            return self._parse_pipeline(payload)
        elif object_kind == "issue":
            return self._parse_issue(payload)
        elif object_kind == "note":
            return self._parse_comment(payload)
        elif object_kind == "tag_push":
            return self._parse_tag_push(payload)
        elif object_kind == "wiki_page":
            return self._parse_wiki(payload)
        else:
            return self._parse_unknown(payload)

    def _parse_push(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse push event"""
        project = payload.get("project", {})
        ref = payload.get("ref", "").replace("refs/heads/", "")

        return ParsedEvent(
            platform="gitlab",
            event_type="push",
            project=project.get("path_with_namespace", ""),
            project_url=project.get("web_url", ""),
            author=payload.get("user_name", "Unknown"),
            author_username=payload.get("user_username", ""),
            author_avatar=payload.get("user_avatar", None),
            ref=ref,
            commits=payload.get("commits", []),
            commit_count=payload.get("total_commits_count", 0),
            raw_data=payload,
        )

    def _parse_merge_request(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse merge request event"""
        user = payload.get("user", {})
        project = payload.get("project", {})
        mr = payload.get("object_attributes", {})

        return ParsedEvent(
            platform="gitlab",
            event_type="merge_request",
            project=project.get("path_with_namespace", ""),
            project_url=project.get("web_url", ""),
            author=user.get("name", "Unknown"),
            author_username=user.get("username", ""),
            author_avatar=user.get("avatar_url", None),
            mr_iid=mr.get("iid"),
            mr_title=mr.get("title", ""),
            mr_description=self._truncate(mr.get("description", "")),
            mr_url=mr.get("url", ""),
            mr_state=mr.get("state", ""),
            mr_action=mr.get("action", ""),
            source_branch=mr.get("source_branch", ""),
            target_branch=mr.get("target_branch", ""),
            raw_data=payload,
        )

    def _parse_pipeline(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse pipeline event"""
        user = payload.get("user", {})
        project = payload.get("project", {})
        pipeline = payload.get("object_attributes", {})

        return ParsedEvent(
            platform="gitlab",
            event_type="pipeline",
            project=project.get("path_with_namespace", ""),
            project_url=project.get("web_url", ""),
            author=user.get("name", "Unknown"),
            author_username=user.get("username", ""),
            author_avatar=user.get("avatar_url", None),
            ref=pipeline.get("ref", ""),
            pipeline_id=pipeline.get("id"),
            pipeline_status=pipeline.get("status", ""),
            pipeline_url=f"{project.get('web_url', '')}/-/pipelines/{pipeline.get('id', '')}",
            pipeline_duration=pipeline.get("duration"),
            pipeline_stages=pipeline.get("stages", []),
            raw_data=payload,
        )

    def _parse_issue(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse issue event"""
        user = payload.get("user", {})
        project = payload.get("project", {})
        issue = payload.get("object_attributes", {})

        return ParsedEvent(
            platform="gitlab",
            event_type="issue",
            project=project.get("path_with_namespace", ""),
            project_url=project.get("web_url", ""),
            author=user.get("name", "Unknown"),
            author_username=user.get("username", ""),
            author_avatar=user.get("avatar_url", None),
            issue_iid=issue.get("iid"),
            issue_title=issue.get("title", ""),
            issue_description=self._truncate(issue.get("description", "")),
            issue_url=issue.get("url", ""),
            issue_state=issue.get("state", ""),
            issue_action=issue.get("action", ""),
            raw_data=payload,
        )

    def _parse_comment(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse comment/note event"""
        user = payload.get("user", {})
        project = payload.get("project", {})
        note = payload.get("object_attributes", {})

        return ParsedEvent(
            platform="gitlab",
            event_type="comment",
            project=project.get("path_with_namespace", ""),
            project_url=project.get("web_url", ""),
            author=user.get("name", "Unknown"),
            author_username=user.get("username", ""),
            author_avatar=user.get("avatar_url", None),
            comment_body=self._truncate(note.get("note", "")),
            comment_url=note.get("url", ""),
            raw_data=payload,
        )

    def _parse_tag_push(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse tag push event"""
        project = payload.get("project", {})
        ref = payload.get("ref", "").replace("refs/tags/", "")

        return ParsedEvent(
            platform="gitlab",
            event_type="tag_push",
            project=project.get("path_with_namespace", ""),
            project_url=project.get("web_url", ""),
            author=payload.get("user_name", "Unknown"),
            author_username=payload.get("user_username", ""),
            ref=ref,
            raw_data=payload,
        )

    def _parse_wiki(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse wiki page event"""
        user = payload.get("user", {})
        project = payload.get("project", {})

        return ParsedEvent(
            platform="gitlab",
            event_type="wiki",
            project=project.get("path_with_namespace", ""),
            project_url=project.get("web_url", ""),
            author=user.get("name", "Unknown"),
            author_username=user.get("username", ""),
            author_avatar=user.get("avatar_url", None),
            raw_data=payload,
        )

    def _parse_unknown(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse unknown event type"""
        project = payload.get("project", {})

        return ParsedEvent(
            platform="gitlab",
            event_type="unknown",
            project=project.get("path_with_namespace", "Unknown"),
            project_url=project.get("web_url", ""),
            author="Unknown",
            author_username="",
            raw_data=payload,
        )
