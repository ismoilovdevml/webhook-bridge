"""Tests for Git platform parsers."""
import pytest
from app.parsers.gitlab import GitLabParser
from app.parsers.github import GitHubParser
from app.parsers.bitbucket import BitbucketParser


class TestGitLabParser:
    """Test GitLab parser."""

    def test_parse_push_event(self):
        """Test parsing GitLab push event."""
        parser = GitLabParser()
        headers = {"X-Gitlab-Event": "Push Hook"}
        payload = {
            "object_kind": "push",
            "project": {
                "path_with_namespace": "test/project",
                "web_url": "https://gitlab.com/test/project"
            },
            "user_name": "testuser",
            "user_username": "testuser",
            "user_avatar": "https://example.com/avatar.png",
            "ref": "refs/heads/main",
            "commits": [
                {"id": "abc123", "message": "Test commit"}
            ],
            "total_commits_count": 1
        }

        result = parser.parse(headers, payload)

        assert result.platform == "gitlab"
        assert result.event_type == "push"
        assert result.project == "test/project"
        assert result.author == "testuser"
        assert result.ref == "main"
        assert len(result.commits) == 1

    def test_parse_merge_request_event(self):
        """Test parsing GitLab merge request event."""
        parser = GitLabParser()
        headers = {"X-Gitlab-Event": "Merge Request Hook"}
        payload = {
            "object_kind": "merge_request",
            "project": {
                "path_with_namespace": "test/project",
                "web_url": "https://gitlab.com/test/project",
            },
            "user": {
                "name": "testuser",
                "username": "testuser",
                "avatar_url": "https://example.com/avatar.png",
            },
            "object_attributes": {
                "iid": 42,
                "title": "Add new feature",
                "description": "This MR adds a new feature",
                "url": "https://gitlab.com/test/project/-/merge_requests/42",
                "state": "opened",
                "action": "open",
                "source_branch": "feature",
                "target_branch": "main",
            },
        }

        result = parser.parse(headers, payload)

        assert result.platform == "gitlab"
        assert result.event_type == "merge_request"
        assert result.mr_iid == 42
        assert result.mr_title == "Add new feature"
        assert result.source_branch == "feature"
        assert result.target_branch == "main"

    def test_parse_pipeline_event(self):
        """Test parsing GitLab pipeline event."""
        parser = GitLabParser()
        headers = {"X-Gitlab-Event": "Pipeline Hook"}
        payload = {
            "object_kind": "pipeline",
            "project": {
                "path_with_namespace": "test/project",
                "web_url": "https://gitlab.com/test/project",
            },
            "user": {
                "name": "testuser",
                "username": "testuser",
                "avatar_url": "https://example.com/avatar.png",
            },
            "object_attributes": {
                "id": 123,
                "status": "success",
                "ref": "main",
                "duration": 300,
                "stages": ["build", "test", "deploy"],
            },
            "commit": {"url": "https://gitlab.com/test/project/commit/abc123"},
        }

        result = parser.parse(headers, payload)

        assert result.platform == "gitlab"
        assert result.event_type == "pipeline"
        assert result.pipeline_id == 123
        assert result.pipeline_status == "success"
        assert result.pipeline_duration == 300

    def test_parse_issue_event(self):
        """Test parsing GitLab issue event."""
        parser = GitLabParser()
        headers = {"X-Gitlab-Event": "Issue Hook"}
        payload = {
            "object_kind": "issue",
            "project": {
                "path_with_namespace": "test/project",
                "web_url": "https://gitlab.com/test/project",
            },
            "user": {
                "name": "testuser",
                "username": "testuser",
                "avatar_url": "https://example.com/avatar.png",
            },
            "object_attributes": {
                "iid": 10,
                "title": "Bug report",
                "description": "Found a bug",
                "url": "https://gitlab.com/test/project/-/issues/10",
                "state": "opened",
                "action": "open",
            },
        }

        result = parser.parse(headers, payload)

        assert result.platform == "gitlab"
        assert result.event_type == "issue"
        assert result.issue_iid == 10
        assert result.issue_title == "Bug report"


class TestGitHubParser:
    """Test GitHub parser."""

    def test_parse_push_event(self):
        """Test parsing GitHub push event."""
        parser = GitHubParser()
        headers = {"X-GitHub-Event": "push"}
        payload = {
            "repository": {
                "full_name": "test/project",
                "html_url": "https://github.com/test/project"
            },
            "sender": {
                "login": "testuser",
                "avatar_url": "https://example.com/avatar.png"
            },
            "pusher": {
                "name": "testuser"
            },
            "ref": "refs/heads/main",
            "commits": [
                {"id": "abc123", "message": "Test commit"}
            ]
        }

        result = parser.parse(headers, payload)

        assert result.platform == "github"
        assert result.event_type == "push"
        assert result.project == "test/project"
        assert result.author == "testuser"
        assert result.ref == "main"

    def test_parse_pull_request_event(self):
        """Test parsing GitHub pull request event."""
        parser = GitHubParser()
        headers = {"X-GitHub-Event": "pull_request"}
        payload = {
            "action": "opened",
            "repository": {
                "full_name": "test/project",
                "html_url": "https://github.com/test/project",
            },
            "sender": {
                "login": "testuser",
                "avatar_url": "https://example.com/avatar.png",
            },
            "pull_request": {
                "number": 42,
                "title": "Add new feature",
                "body": "This PR adds a new feature",
                "html_url": "https://github.com/test/project/pull/42",
                "state": "open",
                "head": {"ref": "feature"},
                "base": {"ref": "main"},
                "user": {"login": "testuser"},
            },
        }

        result = parser.parse(headers, payload)

        assert result.platform == "github"
        assert result.event_type == "pull_request"
        assert result.mr_iid == 42
        assert result.mr_title == "Add new feature"
        assert result.source_branch == "feature"
        assert result.target_branch == "main"

    def test_parse_workflow_run_event(self):
        """Test parsing GitHub workflow run event."""
        parser = GitHubParser()
        headers = {"X-GitHub-Event": "workflow_run"}
        payload = {
            "action": "completed",
            "repository": {
                "full_name": "test/project",
                "html_url": "https://github.com/test/project",
            },
            "sender": {
                "login": "testuser",
                "avatar_url": "https://example.com/avatar.png",
            },
            "workflow_run": {
                "id": 123,
                "conclusion": "success",
                "html_url": "https://github.com/test/project/actions/runs/123",
                "head_branch": "main",
            },
        }

        result = parser.parse(headers, payload)

        assert result.platform == "github"
        assert result.event_type == "workflow"
        assert result.pipeline_id == 123
        assert result.pipeline_status == "success"

    def test_parse_issues_event(self):
        """Test parsing GitHub issues event."""
        parser = GitHubParser()
        headers = {"X-GitHub-Event": "issues"}
        payload = {
            "action": "opened",
            "repository": {
                "full_name": "test/project",
                "html_url": "https://github.com/test/project",
            },
            "sender": {
                "login": "testuser",
                "avatar_url": "https://example.com/avatar.png",
            },
            "issue": {
                "number": 10,
                "title": "Bug report",
                "body": "Found a bug",
                "html_url": "https://github.com/test/project/issues/10",
                "state": "open",
                "user": {"login": "testuser"},
            },
        }

        result = parser.parse(headers, payload)

        assert result.platform == "github"
        assert result.event_type == "issue"
        assert result.issue_iid == 10
        assert result.issue_title == "Bug report"


class TestBitbucketParser:
    """Test Bitbucket parser."""

    def test_parse_push_event(self):
        """Test parsing Bitbucket push event."""
        parser = BitbucketParser()
        headers = {"X-Event-Key": "repo:push"}
        payload = {
            "repository": {
                "full_name": "test/project",
                "links": {
                    "html": {
                        "href": "https://bitbucket.org/test/project"
                    }
                }
            },
            "actor": {
                "display_name": "testuser",
                "username": "testuser",
                "links": {
                    "avatar": {
                        "href": "https://example.com/avatar.png"
                    }
                }
            },
            "push": {
                "changes": [
                    {
                        "new": {"name": "main"},
                        "commits": [
                            {"hash": "abc123", "message": "Test commit"}
                        ]
                    }
                ]
            }
        }

        result = parser.parse(headers, payload)

        assert result.platform == "bitbucket"
        assert result.event_type == "push"
        assert result.project == "test/project"
        assert result.author == "testuser"

    def test_parse_pull_request_event(self):
        """Test parsing Bitbucket pull request event."""
        parser = BitbucketParser()
        headers = {"X-Event-Key": "pullrequest:created"}
        payload = {
            "repository": {
                "full_name": "test/project",
                "links": {"html": {"href": "https://bitbucket.org/test/project"}},
            },
            "actor": {
                "display_name": "testuser",
                "username": "testuser",
                "links": {"avatar": {"href": "https://example.com/avatar.png"}},
            },
            "pullrequest": {
                "id": 42,
                "title": "Add new feature",
                "description": "This PR adds a new feature",
                "links": {"html": {"href": "https://bitbucket.org/test/project/pull-requests/42"}},
                "state": "OPEN",
                "source": {"branch": {"name": "feature"}},
                "destination": {"branch": {"name": "main"}},
                "author": {"display_name": "testuser"},
            },
        }

        result = parser.parse(headers, payload)

        assert result.platform == "bitbucket"
        assert result.event_type == "pullrequest"
        assert result.mr_iid == 42
        assert result.mr_title == "Add new feature"
        assert result.source_branch == "feature"
        assert result.target_branch == "main"

    def test_parse_issue_event(self):
        """Test parsing Bitbucket issue event."""
        parser = BitbucketParser()
        headers = {"X-Event-Key": "issue:created"}
        payload = {
            "repository": {
                "full_name": "test/project",
                "links": {"html": {"href": "https://bitbucket.org/test/project"}},
            },
            "actor": {
                "display_name": "testuser",
                "username": "testuser",
                "links": {"avatar": {"href": "https://example.com/avatar.png"}},
            },
            "issue": {
                "id": 10,
                "title": "Bug report",
                "content": {"raw": "Found a bug"},
                "links": {"html": {"href": "https://bitbucket.org/test/project/issues/10"}},
                "state": "new",
            },
        }

        result = parser.parse(headers, payload)

        assert result.platform == "bitbucket"
        assert result.event_type == "issue"
        assert result.issue_iid == 10
        assert result.issue_title == "Bug report"

    def test_parse_pipeline_event(self):
        """Test parsing Bitbucket pipeline event."""
        parser = BitbucketParser()
        headers = {"X-Event-Key": "pipeline:completed"}
        payload = {
            "repository": {
                "full_name": "test/project",
                "links": {"html": {"href": "https://bitbucket.org/test/project"}},
            },
            "actor": {
                "display_name": "testuser",
                "username": "testuser",
                "links": {"avatar": {"href": "https://example.com/avatar.png"}},
            },
            "pipeline": {
                "build_number": 123,
                "state": {"name": "SUCCESSFUL"},
                "target": {"ref_name": "main"},
                "duration_in_seconds": 300,
                "url": "https://bitbucket.org/test/project/pipelines/results/123",
            },
        }

        result = parser.parse(headers, payload)

        assert result.platform == "bitbucket"
        assert result.event_type == "pipeline"
        assert result.pipeline_id == 123
        assert result.pipeline_status == "success"
        assert result.ref == "main"
        assert result.pipeline_duration == 300
