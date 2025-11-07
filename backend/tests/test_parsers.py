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
