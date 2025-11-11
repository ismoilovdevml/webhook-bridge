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
        event_type = payload.get("event_type", "")

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
        elif object_kind == "work_item":  # GitLab 17+ Work Items
            return self._parse_work_item(payload)
        elif event_type == "confidential_note":  # Confidential comments
            return self._parse_confidential_comment(payload)
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
        elif event_name in [
            "user_add_to_group", "user_update_for_group",
            "user_remove_from_group", "user_access_request_to_group",
            "user_access_request_denied_for_group"
        ]:
            return self._parse_member(payload)
        elif event_name in ["project_create", "project_destroy"]:
            return self._parse_project_event(payload)
        elif event_name in ["subgroup_create", "subgroup_destroy"]:
            return self._parse_subgroup(payload)
        elif object_kind == "milestone":
            return self._parse_milestone(payload)
        elif object_kind == "vulnerability":
            return self._parse_vulnerability(payload)
        elif event_name == "repository_update":  # Repository updates
            return self._parse_repository_update(payload)
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
        action = mr.get("action", "")

        # Determine event type based on action
        if action in ["approval", "approved", "unapproval", "unapproved"]:
            event_type = "merge_request_approval"
        else:
            event_type = "merge_request"

        # Extract approval information
        approved = mr.get("approved", False)
        approvals_required = mr.get("approvals_required", 0)
        approvals_left = mr.get("approvals_left", 0)

        return ParsedEvent(
            platform="gitlab",
            event_type=event_type,
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
            mr_action=action,
            mr_approved=approved,
            mr_approvals_required=approvals_required,
            mr_approvals_left=approvals_left,
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

        # Check if issue is confidential
        is_confidential = issue.get("confidential", False)

        # Check if it's a service desk issue
        is_service_desk = issue.get("service_desk_reply_to") is not None

        return ParsedEvent(
            platform="gitlab",
            event_type="confidential_issue" if is_confidential else "issue",
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
            issue_confidential=is_confidential,
            issue_service_desk=is_service_desk,
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

        # Extract author info
        author_obj = release.get("author", {})
        author_name = (
            author_obj.get("name", "Unknown")
            if isinstance(author_obj, dict)
            else "Unknown"
        )
        author_user = (
            author_obj.get("username", "")
            if isinstance(author_obj, dict)
            else ""
        )

        # Extract release URL
        links = release.get("_links", {})
        rel_url = links.get("self", "") if isinstance(links, dict) else ""

        return ParsedEvent(
            platform="gitlab",
            event_type="release",
            project=project.get("path_with_namespace", ""),
            project_url=project.get("web_url", ""),
            author=author_name,
            author_username=author_user,
            ref=release.get("tag_name", ""),
            release_name=release.get("name", ""),
            release_tag=release.get("tag_name", ""),
            release_description=self._truncate(release.get("description", "")),
            release_url=rel_url,
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

    def _parse_member(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse group member event"""
        event_name = payload.get("event_name", "")

        # Determine action from event_name
        if "add" in event_name:
            action = "added"
        elif "update" in event_name:
            action = "updated"
        elif "remove" in event_name:
            action = "removed"
        elif "request" in event_name and "denied" not in event_name:
            action = "requested"
        elif "denied" in event_name:
            action = "denied"
        else:
            action = event_name

        return ParsedEvent(
            platform="gitlab",
            event_type="member",
            project=payload.get("group_path", "Group"),
            project_url=f"https://gitlab.com/{payload.get('group_path', '')}",
            author=payload.get("user_name", "Unknown"),
            author_username=payload.get("user_username", ""),
            member_username=payload.get("user_username", ""),
            member_role=payload.get("group_access", ""),
            member_action=action,
            raw_data=payload,
        )

    def _parse_project_event(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse project create/destroy event"""
        event_name = payload.get("event_name", "")
        action = "created" if "create" in event_name else "deleted"

        return ParsedEvent(
            platform="gitlab",
            event_type="project",
            project=payload.get("path_with_namespace", ""),
            project_url="",
            author=payload.get("owners", [{}])[0].get("name", "Unknown"),
            author_username="",
            repo_action=action,
            repo_visibility=payload.get("project_visibility", ""),
            raw_data=payload,
        )

    def _parse_subgroup(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse subgroup create/destroy event"""
        event_name = payload.get("event_name", "")
        action = "created" if "create" in event_name else "deleted"

        return ParsedEvent(
            platform="gitlab",
            event_type="subgroup",
            project=payload.get("full_path", ""),
            project_url="",
            author="System",
            author_username="",
            team_name=payload.get("name", ""),
            team_action=action,
            raw_data=payload,
        )

    def _parse_milestone(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse milestone event"""
        user = payload.get("user", {})
        project = payload.get("project", {})
        milestone = payload.get("object_attributes", {})

        return ParsedEvent(
            platform="gitlab",
            event_type="milestone",
            project=project.get("path_with_namespace", ""),
            project_url=project.get("web_url", ""),
            author=user.get("name", "Unknown"),
            author_username=user.get("username", ""),
            author_avatar=user.get("avatar_url", None),
            milestone_id=milestone.get("id"),
            milestone_title=milestone.get("title", ""),
            milestone_description=self._truncate(
                milestone.get("description", "")
            ),
            milestone_state=milestone.get("state", ""),
            milestone_due_date=milestone.get("due_date", ""),
            milestone_action=payload.get("action", ""),
            raw_data=payload,
        )

    def _parse_vulnerability(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse vulnerability event"""
        vulnerability = payload.get("object_attributes", {})

        # Map severity from GitLab to standard levels
        severity = vulnerability.get("severity", "unknown").lower()

        return ParsedEvent(
            platform="gitlab",
            event_type="vulnerability",
            project=vulnerability.get("project_id", ""),
            project_url="",
            author="Security Scanner",
            author_username="",
            alert_id=vulnerability.get("id"),
            alert_type="vulnerability",
            alert_severity=severity,
            alert_state=vulnerability.get("state", ""),
            alert_url=vulnerability.get("url", ""),
            alert_description=self._truncate(vulnerability.get("title", "")),
            raw_data=payload,
        )

    def _parse_work_item(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse work item event (GitLab 17+)"""
        user = payload.get("user", {})
        project = payload.get("project", {})
        work_item = payload.get("object_attributes", {})

        # Work items can be: Epic, Task, OKR, Test Case, Requirement, etc.
        work_item_type = work_item.get("type", "WorkItem")
        is_confidential = work_item.get("confidential", False)

        return ParsedEvent(
            platform="gitlab",
            event_type="work_item",
            project=project.get("path_with_namespace", ""),
            project_url=project.get("web_url", ""),
            author=user.get("name", "Unknown"),
            author_username=user.get("username", ""),
            author_avatar=user.get("avatar_url", None),
            issue_iid=work_item.get("iid"),
            issue_title=work_item.get("title", ""),
            issue_description=self._truncate(work_item.get("description", "")),
            issue_url=work_item.get("url", ""),
            issue_state=work_item.get("state", ""),
            issue_action=work_item.get("action", ""),
            issue_confidential=is_confidential,
            work_item_type=work_item_type,
            raw_data=payload,
        )

    def _parse_confidential_comment(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse confidential comment/note event"""
        user = payload.get("user", {})
        project = payload.get("project", {})
        note = payload.get("object_attributes", {})

        return ParsedEvent(
            platform="gitlab",
            event_type="confidential_comment",
            project=project.get("path_with_namespace", ""),
            project_url=project.get("web_url", ""),
            author=user.get("name", "Unknown"),
            author_username=user.get("username", ""),
            author_avatar=user.get("avatar_url", None),
            comment_body=self._truncate(note.get("note", "")),
            comment_url=note.get("url", ""),
            comment_confidential=True,
            raw_data=payload,
        )

    def _parse_repository_update(self, payload: Dict[str, Any]) -> ParsedEvent:
        """Parse repository update event"""
        project = payload.get("project", {})
        user = payload.get("user", {})

        # Repository updates include changes not related to push/MR
        # Like repository settings, default branch changes, etc.
        changes = payload.get("changes", [])

        return ParsedEvent(
            platform="gitlab",
            event_type="repository_update",
            project=project.get("path_with_namespace", ""),
            project_url=project.get("web_url", ""),
            author=user.get("name", "Unknown") if user else "System",
            author_username=user.get("username", "") if user else "",
            repo_changes=changes,
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
