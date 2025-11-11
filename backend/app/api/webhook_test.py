"""Webhook testing API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel

from ..database import get_db
from ..models.provider import Provider
from ..parsers import get_parser
from ..providers import get_provider
from ..formatters import HTMLFormatter, MarkdownFormatter, SlackBlocksFormatter
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/webhook-test", tags=["webhook-test"])


# Sample webhook payloads for testing
SAMPLE_PAYLOADS = {
    "gitlab_push": {
        "object_kind": "push",
        "event_name": "push",
        "before": "95790bf891e76fee5e1747ab589903a6a1f80f22",
        "after": "da1560886d4f094c3e6c9ef40349f7d38b5d27d7",
        "ref": "refs/heads/main",
        "user_name": "John Doe",
        "user_username": "johndoe",
        "user_avatar": "https://gitlab.com/uploads/user/avatar/123/avatar.png",
        "project": {
            "id": 15,
            "name": "Webhook Bridge",
            "path_with_namespace": "myorg/webhook-bridge",
            "web_url": "https://gitlab.com/myorg/webhook-bridge"
        },
        "commits": [
            {
                "id": "da1560886d4f094c3e6c9ef40349f7d38b5d27d7",
                "message": "Fix critical bug in webhook processing",
                "timestamp": "2025-01-10T10:30:00+00:00",
                "author": {
                    "name": "John Doe",
                    "email": "john@example.com"
                }
            }
        ],
        "total_commits_count": 1
    },

    "github_push": {
        "ref": "refs/heads/main",
        "before": "95790bf891e76fee5e1747ab589903a6a1f80f22",
        "after": "da1560886d4f094c3e6c9ef40349f7d38b5d27d7",
        "repository": {
            "id": 123456,
            "name": "webhook-bridge",
            "full_name": "myorg/webhook-bridge",
            "html_url": "https://github.com/myorg/webhook-bridge"
        },
        "pusher": {
            "name": "John Doe",
            "email": "john@example.com"
        },
        "sender": {
            "login": "johndoe",
            "avatar_url": "https://avatars.githubusercontent.com/u/123456"
        },
        "commits": [
            {
                "id": "da1560886d4f094c3e6c9ef40349f7d38b5d27d7",
                "message": "Fix critical bug in webhook processing",
                "timestamp": "2025-01-10T10:30:00+00:00",
                "author": {
                    "name": "John Doe",
                    "email": "john@example.com"
                }
            }
        ]
    },

    "gitlab_merge_request": {
        "object_kind": "merge_request",
        "user": {
            "name": "John Doe",
            "username": "johndoe",
            "avatar_url": "https://gitlab.com/uploads/user/avatar/123/avatar.png"
        },
        "project": {
            "id": 15,
            "name": "Webhook Bridge",
            "path_with_namespace": "myorg/webhook-bridge",
            "web_url": "https://gitlab.com/myorg/webhook-bridge"
        },
        "object_attributes": {
            "iid": 42,
            "title": "Add new notification templates",
            "description": "This MR adds support for customizable Jinja2 templates",
            "url": "https://gitlab.com/myorg/webhook-bridge/-/merge_requests/42",
            "state": "opened",
            "action": "open",
            "source_branch": "feature/templates",
            "target_branch": "main"
        }
    }
}


class WebhookTestRequest(BaseModel):
    """Request model for webhook testing."""
    platform: str  # gitlab, github, bitbucket
    event_type: str  # push, merge_request, etc.
    provider_id: int | None = None
    custom_payload: Dict[str, Any] | None = None


class WebhookTestResponse(BaseModel):
    """Response model for webhook testing."""
    success: bool
    message: str
    parsed_event: Dict[str, Any] | None = None
    formatted_message: Dict[str, Any] | None = None
    provider_result: str | None = None


@router.get("/samples", summary="Get sample webhook payloads")
def get_sample_payloads() -> Dict[str, Any]:
    """
    Get sample webhook payloads for testing.

    Returns dictionary of sample payloads for different platforms and event types.
    """
    return {
        "samples": list(SAMPLE_PAYLOADS.keys()),
        "payloads": SAMPLE_PAYLOADS
    }


@router.get("/samples/{sample_name}", summary="Get specific sample payload")
def get_sample_payload(sample_name: str) -> Dict[str, Any]:
    """Get a specific sample webhook payload."""
    if sample_name not in SAMPLE_PAYLOADS:
        raise HTTPException(
            status_code=404,
            detail=f"Sample '{sample_name}' not found. Available: {list(SAMPLE_PAYLOADS.keys())}"
        )
    return SAMPLE_PAYLOADS[sample_name]


@router.post("/parse", summary="Test webhook parsing")
def test_webhook_parsing(
    request: WebhookTestRequest
) -> Dict[str, Any]:
    """
    Test webhook parsing without sending to providers.

    Useful for testing parser logic and seeing what data is extracted.
    """
    try:
        # Get payload
        if request.custom_payload:
            payload = request.custom_payload
        else:
            # Try to find matching sample
            sample_key = f"{request.platform}_{request.event_type}"
            if sample_key not in SAMPLE_PAYLOADS:
                raise HTTPException(
                    status_code=400,
                    detail=f"No sample payload for {sample_key}. Provide custom_payload."
                )
            payload = SAMPLE_PAYLOADS[sample_key]

        # Create fake headers based on platform
        if request.platform == "gitlab":
            headers = {"x-gitlab-event": request.event_type}
        elif request.platform == "github":
            headers = {"x-github-event": request.event_type}
        elif request.platform == "bitbucket":
            headers = {"x-event-key": f"repo:{request.event_type}"}
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported platform: {request.platform}"
            )

        # Parse webhook
        parser = get_parser(headers)
        parsed_event = parser.parse(headers, payload)

        return {
            "success": True,
            "platform": parsed_event.platform,
            "event_type": parsed_event.event_type,
            "parsed_data": {
                "project": parsed_event.project,
                "author": parsed_event.author,
                "ref": parsed_event.ref,
                # Add other relevant fields
            },
            "full_parsed_event": parsed_event.__dict__
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error testing webhook parsing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/format", summary="Test message formatting")
def test_message_formatting(
    request: WebhookTestRequest,
    format_type: str = "markdown"
) -> Dict[str, Any]:
    """
    Test message formatting without sending.

    Args:
        format_type: Format type (markdown, html, slack_blocks)
    """
    try:
        # First parse the webhook
        parse_result = test_webhook_parsing(request)
        parsed_event_dict = parse_result["full_parsed_event"]

        # Reconstruct parsed event object (simplified)
        from ..parsers.base import ParsedEvent
        parsed_event = ParsedEvent(**parsed_event_dict)

        # Format message
        if format_type == "html":
            formatter = HTMLFormatter()
        elif format_type == "slack_blocks":
            formatter = SlackBlocksFormatter()
        else:
            formatter = MarkdownFormatter()

        formatted_message = formatter.format(parsed_event)

        return {
            "success": True,
            "format_type": format_type,
            "formatted_message": formatted_message
        }

    except Exception as e:
        logger.error(f"Error testing message formatting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send", summary="Test webhook end-to-end")
async def test_webhook_send(
    request: WebhookTestRequest,
    db: Session = Depends(get_db)
) -> WebhookTestResponse:
    """
    Test webhook end-to-end: parse, format, and send to provider.

    Requires provider_id to send actual notification.
    """
    try:
        # Validate provider
        if not request.provider_id:
            raise HTTPException(
                status_code=400,
                detail="provider_id required for send test"
            )

        provider_model = db.query(Provider).filter(
            Provider.id == request.provider_id
        ).first()

        if not provider_model:
            raise HTTPException(status_code=404, detail="Provider not found")

        # Parse webhook
        parse_result = test_webhook_parsing(request)
        parsed_event_dict = parse_result["full_parsed_event"]

        from ..parsers.base import ParsedEvent
        parsed_event = ParsedEvent(**parsed_event_dict)

        # Format message
        formatter_map = {
            "telegram": HTMLFormatter(),
            "slack": SlackBlocksFormatter(),
            "discord": MarkdownFormatter(),
            "mattermost": MarkdownFormatter(),
        }

        formatter = formatter_map.get(provider_model.type, MarkdownFormatter())
        formatted_message = formatter.format(parsed_event)

        # Send to provider
        decrypted_config = provider_model.get_decrypted_config()
        provider = get_provider(provider_model.type, decrypted_config)

        success = await provider.send(formatted_message)

        return WebhookTestResponse(
            success=success,
            message="Test notification sent successfully" if success else "Failed to send",
            parsed_event=parse_result["parsed_data"],
            formatted_message=formatted_message,
            provider_result="Sent" if success else "Failed"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing webhook send: {e}")
        raise HTTPException(status_code=500, detail=str(e))
