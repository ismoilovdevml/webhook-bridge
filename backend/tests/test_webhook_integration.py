"""Integration tests for webhook processing flow."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.models.provider import Provider
from app.models.event import Event


client = TestClient(app)


class TestWebhookIntegration:
    """Test complete webhook processing flow."""

    @pytest.mark.asyncio
    async def test_gitlab_push_webhook_flow(self, db_session):
        """Test complete GitLab push webhook processing."""
        # Create a test provider
        provider = Provider(
            name="Test Telegram",
            type="telegram",
            config={"bot_token": "123:ABC", "chat_id": "-100123"},
            active=True,
        )
        db_session.add(provider)
        db_session.commit()

        # GitLab push webhook payload
        headers = {"x-gitlab-event": "Push Hook"}
        payload = {
            "object_kind": "push",
            "ref": "refs/heads/main",
            "project": {
                "name": "Test Project",
                "path_with_namespace": "test/project",
                "web_url": "https://gitlab.com/test/project",
            },
            "user_name": "Test User",
            "user_username": "testuser",
            "user_avatar": "https://gitlab.com/avatar.png",
            "commits": [
                {
                    "id": "abc123",
                    "message": "Test commit",
                    "url": "https://gitlab.com/test/project/commit/abc123",
                    "author": {"name": "Test User", "email": "test@example.com"},
                }
            ],
            "total_commits_count": 1,
        }

        # Mock provider send method
        with patch(
            "app.providers.telegram.TelegramProvider.send", new_callable=AsyncMock
        ) as mock_send:
            mock_send.return_value = True

            response = client.post("/webhook/git", headers=headers, json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["event"]["platform"] == "gitlab"
            assert data["event"]["type"] == "push"
            assert data["providers"] == 1

            # Wait a bit for background task
            import time

            time.sleep(0.5)

            # Verify provider was called
            mock_send.assert_called_once()

            # Verify event was logged
            events = db_session.query(Event).all()
            assert len(events) == 1
            assert events[0].platform == "gitlab"
            assert events[0].event_type == "push"
            assert events[0].branch == "refs/heads/main"

    @pytest.mark.asyncio
    async def test_github_pull_request_webhook(self, db_session):
        """Test GitHub pull request webhook."""
        provider = Provider(
            name="Test Slack",
            type="slack",
            config={"webhook_url": "https://hooks.slack.com/test"},
            active=True,
        )
        db_session.add(provider)
        db_session.commit()

        headers = {"x-github-event": "pull_request"}
        payload = {
            "action": "opened",
            "pull_request": {
                "number": 42,
                "title": "Add new feature",
                "body": "This PR adds a new feature",
                "html_url": "https://github.com/test/repo/pull/42",
                "state": "open",
                "head": {"ref": "feature-branch"},
                "base": {"ref": "main"},
                "user": {
                    "login": "testuser",
                    "avatar_url": "https://github.com/avatar.png",
                },
            },
            "repository": {
                "name": "repo",
                "full_name": "test/repo",
                "html_url": "https://github.com/test/repo",
            },
            "sender": {"login": "testuser"},
        }

        with patch(
            "app.providers.slack.SlackProvider.send", new_callable=AsyncMock
        ) as mock_send:
            mock_send.return_value = True

            response = client.post("/webhook/git", headers=headers, json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["event"]["platform"] == "github"
            assert data["event"]["type"] == "pull_request"

    @pytest.mark.asyncio
    async def test_webhook_with_no_active_providers(self, db_session):
        """Test webhook when no providers are active."""
        # Create inactive provider
        provider = Provider(
            name="Inactive Provider",
            type="telegram",
            config={"bot_token": "123:ABC", "chat_id": "-100123"},
            active=False,
        )
        db_session.add(provider)
        db_session.commit()

        headers = {"x-gitlab-event": "Push Hook"}
        payload = {
            "object_kind": "push",
            "ref": "refs/heads/main",
            "project": {
                "name": "Test",
                "path_with_namespace": "test/test",
                "web_url": "https://gitlab.com/test/test",
            },
            "user_name": "Test",
            "user_username": "test",
            "commits": [],
            "total_commits_count": 0,
        }

        response = client.post("/webhook/git", headers=headers, json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
        assert "no active providers" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_webhook_with_invalid_platform(self):
        """Test webhook with unknown platform."""
        headers = {}  # No platform headers
        payload = {"test": "data"}

        response = client.post("/webhook/git", headers=headers, json=payload)

        assert response.status_code == 400
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_webhook_with_invalid_json(self):
        """Test webhook with invalid JSON."""
        headers = {"x-gitlab-event": "Push Hook"}

        response = client.post(
            "/webhook/git",
            data="invalid json",
            headers={**headers, "Content-Type": "application/json"},
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_multiple_providers_receive_webhook(self, db_session):
        """Test that all active providers receive the webhook."""
        # Create multiple providers
        telegram_provider = Provider(
            name="Telegram",
            type="telegram",
            config={"bot_token": "123:ABC", "chat_id": "-100123"},
            active=True,
        )
        slack_provider = Provider(
            name="Slack",
            type="slack",
            config={"webhook_url": "https://hooks.slack.com/test"},
            active=True,
        )
        db_session.add(telegram_provider)
        db_session.add(slack_provider)
        db_session.commit()

        headers = {"x-gitlab-event": "Push Hook"}
        payload = {
            "object_kind": "push",
            "ref": "refs/heads/main",
            "project": {
                "name": "Test",
                "path_with_namespace": "test/test",
                "web_url": "https://gitlab.com/test/test",
            },
            "user_name": "Test",
            "user_username": "test",
            "commits": [],
            "total_commits_count": 0,
        }

        with patch(
            "app.providers.telegram.TelegramProvider.send", new_callable=AsyncMock
        ) as mock_telegram, patch(
            "app.providers.slack.SlackProvider.send", new_callable=AsyncMock
        ) as mock_slack:
            mock_telegram.return_value = True
            mock_slack.return_value = True

            response = client.post("/webhook/git", headers=headers, json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data["providers"] == 2

            # Wait for background tasks
            import time

            time.sleep(0.5)

            # Both providers should be called
            mock_telegram.assert_called_once()
            mock_slack.assert_called_once()

            # Two events should be logged
            events = db_session.query(Event).all()
            assert len(events) == 2

    @pytest.mark.asyncio
    async def test_provider_failure_is_logged(self, db_session):
        """Test that provider failures are logged correctly."""
        provider = Provider(
            name="Failing Provider",
            type="telegram",
            config={"bot_token": "123:ABC", "chat_id": "-100123"},
            active=True,
        )
        db_session.add(provider)
        db_session.commit()

        headers = {"x-gitlab-event": "Push Hook"}
        payload = {
            "object_kind": "push",
            "ref": "refs/heads/main",
            "project": {
                "name": "Test",
                "path_with_namespace": "test/test",
                "web_url": "https://gitlab.com/test/test",
            },
            "user_name": "Test",
            "user_username": "test",
            "commits": [],
            "total_commits_count": 0,
        }

        # Mock provider to fail
        with patch(
            "app.providers.telegram.TelegramProvider.send", new_callable=AsyncMock
        ) as mock_send:
            mock_send.side_effect = Exception("Network error")

            response = client.post("/webhook/git", headers=headers, json=payload)

            assert response.status_code == 200  # Webhook accepted

            # Wait for background task
            import time

            time.sleep(0.5)

            # Event should be logged with failure status
            events = db_session.query(Event).all()
            assert len(events) == 1
            assert events[0].status == "failed"
            assert "Network error" in events[0].error_message


class TestWebhookTest:
    """Test webhook test endpoint."""

    def test_webhook_test_endpoint(self):
        """Test /webhook/test endpoint."""
        response = client.get("/webhook/test")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["message"] == "Webhook service is running"
        assert "version" in data
