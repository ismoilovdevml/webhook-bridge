"""Tests for event filtering logic."""

import pytest
from app.models.provider import Provider


class TestEventFiltering:
    """Test Provider.should_notify() filtering logic."""

    def test_no_filters_always_notify(self):
        """Test that providers without filters notify for all events."""
        provider = Provider(
            name="Test",
            type="telegram",
            config={},
            filters=None,
        )

        # Should notify for any combination
        assert provider.should_notify("github", "push", "my-repo", "main") is True
        assert provider.should_notify("gitlab", "merge_request", "other-repo") is True
        assert provider.should_notify("bitbucket", "pull_request", "test") is True

    def test_empty_filters_always_notify(self):
        """Test that providers with empty filters notify for all events."""
        provider = Provider(
            name="Test",
            type="telegram",
            config={},
            filters={},
        )

        assert provider.should_notify("github", "push", "my-repo", "main") is True

    def test_platform_filter_match(self):
        """Test platform filtering allows matching platforms."""
        provider = Provider(
            name="Test",
            type="telegram",
            config={},
            filters={"platforms": ["github", "gitlab"]},
        )

        assert provider.should_notify("github", "push", "repo") is True
        assert provider.should_notify("gitlab", "push", "repo") is True
        assert provider.should_notify("bitbucket", "push", "repo") is False

    def test_event_type_filter_match(self):
        """Test event type filtering allows matching events."""
        provider = Provider(
            name="Test",
            type="telegram",
            config={},
            filters={"event_types": ["push", "tag"]},
        )

        assert provider.should_notify("github", "push", "repo") is True
        assert provider.should_notify("github", "tag", "repo") is True
        assert provider.should_notify("github", "pull_request", "repo") is False

    def test_project_filter_exact_match(self):
        """Test project filtering with exact matches."""
        provider = Provider(
            name="Test",
            type="telegram",
            config={},
            filters={"projects": ["my-repo", "other-repo"]},
        )

        assert provider.should_notify("github", "push", "my-repo") is True
        assert provider.should_notify("github", "push", "other-repo") is True
        assert provider.should_notify("github", "push", "unknown-repo") is False

    def test_project_filter_wildcard(self):
        """Test project filtering with wildcard patterns."""
        provider = Provider(
            name="Test",
            type="telegram",
            config={},
            filters={"projects": ["frontend-*", "*-api"]},
        )

        assert provider.should_notify("github", "push", "frontend-app") is True
        assert provider.should_notify("github", "push", "frontend-web") is True
        assert provider.should_notify("github", "push", "backend-api") is True
        assert provider.should_notify("github", "push", "mobile-app") is False

    def test_branch_filter_match(self):
        """Test branch filtering allows matching branches."""
        provider = Provider(
            name="Test",
            type="telegram",
            config={},
            filters={"branches": ["main", "develop", "staging"]},
        )

        assert (
            provider.should_notify("github", "push", "repo", "main") is True
        )
        assert (
            provider.should_notify("github", "push", "repo", "develop") is True
        )
        assert (
            provider.should_notify("github", "push", "repo", "feature/test")
            is False
        )

    def test_branch_filter_no_branch_provided(self):
        """Test branch filter when no branch is provided."""
        provider = Provider(
            name="Test",
            type="telegram",
            config={},
            filters={"branches": ["main"]},
        )

        # When no branch provided, should still notify
        assert provider.should_notify("github", "tag", "repo") is True

    def test_combined_filters_all_match(self):
        """Test multiple filters all matching."""
        provider = Provider(
            name="Test",
            type="telegram",
            config={},
            filters={
                "platforms": ["github"],
                "event_types": ["push"],
                "projects": ["my-repo"],
                "branches": ["main"],
            },
        )

        # All filters match
        assert (
            provider.should_notify("github", "push", "my-repo", "main") is True
        )

        # Platform doesn't match
        assert (
            provider.should_notify("gitlab", "push", "my-repo", "main") is False
        )

        # Event type doesn't match
        assert (
            provider.should_notify("github", "tag", "my-repo", "main") is False
        )

        # Project doesn't match
        assert (
            provider.should_notify("github", "push", "other-repo", "main")
            is False
        )

        # Branch doesn't match
        assert (
            provider.should_notify("github", "push", "my-repo", "develop")
            is False
        )

    def test_empty_filter_lists(self):
        """Test that empty filter lists allow all."""
        provider = Provider(
            name="Test",
            type="telegram",
            config={},
            filters={
                "platforms": [],
                "event_types": [],
                "projects": [],
                "branches": [],
            },
        )

        # Empty lists should allow all
        assert provider.should_notify("github", "push", "any-repo", "main") is True

    def test_partial_filters(self):
        """Test filters with only some criteria specified."""
        provider = Provider(
            name="Test",
            type="telegram",
            config={},
            filters={
                "platforms": ["github"],
                # No event_types, projects, or branches
            },
        )

        # Platform must match, everything else is allowed
        assert provider.should_notify("github", "push", "any-repo") is True
        assert provider.should_notify("github", "tag", "other-repo") is True
        assert provider.should_notify("gitlab", "push", "any-repo") is False

    def test_case_sensitive_matching(self):
        """Test that filtering is case-sensitive."""
        provider = Provider(
            name="Test",
            type="telegram",
            config={},
            filters={"platforms": ["GitHub"]},  # Capital G
        )

        # Should not match due to case difference
        assert provider.should_notify("github", "push", "repo") is False
        assert provider.should_notify("GitHub", "push", "repo") is True
