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
        elif object_kind == "build":  # Job events
            return self._parse_job(payload)
        elif object_kind == "issue":
            return self._parse_issue(payload)
        elif object_kind == "note":
            return self._parse_comment(payload)
        elif object_kind == "tag_push":
            return self._parse_tag_push(payload)
        elif object_kind == "wiki_page":
            return self._parse_wiki(payload)
        elif object_kind == "deployment":
            return self._parse_deployment(payload)
        elif object_kind == "release":
            return self._parse_release(payload)
        elif object_kind == "feature_flag":
            return self._parse_feature_flag(payload)
        elif object_kind == "emoji":
            return self._parse_emoji(payload)
        elif object_kind == "access_token":
            return self._parse_access_token(payload)
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

    def _parse_deployment(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse deployment event"""
        user = payload.get("user", {})
        project = payload.get("project", {})
        deployment = payload.get("deployment", {})

        return ParsedEvent(
            platform="gitlab",
            event_type="deployment",
            project=project.get("path_with_namespace", ""),
            project_url=project.get("web_url", ""),
            author=user.get("name", "Unknown"),
            author_username=user.get("username", ""),
            author_avatar=user.get("avatar_url", None),
            ref=deployment.get("ref", ""),
            deployment_id=deployment.get("id"),
            deployment_status=payload.get("status", ""),
            deployment_environment=deployment.get("environment", ""),
            deployment_url=deployment.get("deployable_url", ""),
            raw_data=payload,
        )

    def _parse_release(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse release event"""
        project = payload.get("project", {})
        release = payload.get("release", {}) if "release" in payload else payload

        return ParsedEvent(
            platform="gitlab",
            event_type="release",
            project=project.get("path_with_namespace", ""),
            project_url=project.get("web_url", ""),
            author=release.get("author", {}).get("name", "Unknown") if isinstance(release.get("author"), dict) else "Unknown",
            author_username=release.get("author", {}).get("username", "") if isinstance(release.get("author"), dict) else "",
            ref=release.get("tag_name", ""),
            release_name=release.get("name", ""),
            release_tag=release.get("tag_name", ""),
            release_description=self._truncate(release.get("description", "")),
            release_url=release.get("_links", {}).get("self", "") if isinstance(release.get("_links"), dict) else "",
            raw_data=payload,
        )

    def _parse_job(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse job/build event"""
        project = payload.get("project", {})
        user = payload.get("user", {})

        return ParsedEvent(
            platform="gitlab",
            event_type="job",
            project=project.get("path_with_namespace", ""),
            project_url=project.get("web_url", ""),
            author=user.get("name", "Unknown"),
            author_username=user.get("username", ""),
            ref=payload.get("ref", ""),
            job_id=payload.get("build_id"),
            job_name=payload.get("build_name", ""),
            job_stage=payload.get("build_stage", ""),
            job_status=payload.get("build_status", ""),
            pipeline_id=payload.get("pipeline_id"),
            raw_data=payload,
        )

    def _parse_feature_flag(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse feature flag event"""
        project = payload.get("project", {})
        user = payload.get("user", {})
        flag = payload.get("object_attributes", {})

        return ParsedEvent(
            platform="gitlab",
            event_type="feature_flag",
            project=project.get("path_with_namespace", ""),
            project_url=project.get("web_url", ""),
            author=user.get("name", "Unknown"),
            author_username=user.get("username", ""),
            feature_flag_name=flag.get("name", ""),
            feature_flag_description=self._truncate(flag.get("description", "")),
            feature_flag_active=flag.get("active", False),
            raw_data=payload,
        )

    def _parse_emoji(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse emoji event"""
        project = payload.get("project", {})
        user = payload.get("user", {})
        emoji = payload.get("object_attributes", {})

        return ParsedEvent(
            platform="gitlab",
            event_type="emoji",
            project=project.get("path_with_namespace", ""),
            project_url=project.get("web_url", ""),
            author=user.get("name", "Unknown"),
            author_username=user.get("username", ""),
            emoji_name=emoji.get("name", ""),
            emoji_action=emoji.get("action", ""),
            emoji_awardable_type=emoji.get("awardable_type", ""),
            raw_data=payload,
        )

    def _parse_access_token(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse access token event"""
        project = payload.get("project", {})
        token = payload.get("object_attributes", {})

        return ParsedEvent(
            platform="gitlab",
            event_type="access_token",
            project=project.get("path_with_namespace", ""),
            project_url=project.get("web_url", ""),
            author="System",
            author_username="",
            token_name=token.get("name", ""),
            token_expires_at=token.get("expires_at", ""),
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
