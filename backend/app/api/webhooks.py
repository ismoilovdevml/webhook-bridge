"""Webhook receiver API endpoints."""

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Depends
from typing import Any, Dict, cast
from datetime import datetime
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.provider import Provider
from ..models.event import Event
from ..parsers import get_parser
from ..providers import get_provider
from ..formatters import (
    HTMLFormatter,
    MarkdownFormatter,
    SlackBlocksFormatter,
    BaseFormatter,
)
from ..utils.logger import get_logger
from ..utils.exceptions import ParserError, ProviderError, FormatterError

logger = get_logger(__name__)
router = APIRouter()


# Formatter mapping for each provider type
FORMATTER_MAP = {
    "telegram": HTMLFormatter(),
    "slack": SlackBlocksFormatter(),
    "mattermost": MarkdownFormatter(),
    "discord": MarkdownFormatter(),
}


async def process_and_send(
    parsed_event: Any, provider_model: Provider, db: Session
) -> None:
    """
    Process and send notification to a provider.

    Args:
        parsed_event: Parsed webhook event
        provider_model: Provider database model
        db: Database session
    """
    event_log = Event(
        platform=parsed_event.platform,
        event_type=parsed_event.event_type,
        project=parsed_event.project,
        author=parsed_event.author,
        branch=parsed_event.ref,  # ref contains branch/tag name
        provider_id=provider_model.id,
        status="pending",
        created_at=datetime.utcnow(),
    )

    try:
        # Get formatter for provider type
        provider_type = cast(str, provider_model.type)
        provider_config = cast(Dict[Any, Any], provider_model.config)

        formatter = cast(BaseFormatter, FORMATTER_MAP.get(provider_type))
        if not formatter:
            raise FormatterError(f"No formatter for provider type: {provider_type}")

        # Format message
        formatted_message = formatter.format(parsed_event)

        # Get provider instance and send
        provider = get_provider(provider_type, provider_config)
        success = await provider.send(formatted_message)

        if success:
            event_log.status = "success"
            logger.info(
                f"Sent {parsed_event.event_type} notification to "
                f"{provider_model.name} ({provider_type})"
            )
        else:
            event_log.status = "failed"
            event_log.error_message = "Provider returned False"

    except (ProviderError, FormatterError) as e:
        event_log.status = "failed"
        event_log.error_message = str(e)
        logger.error(f"Failed to send to {provider_model.name}: {e}")

    except Exception as e:
        event_log.status = "failed"
        event_log.error_message = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error sending to {provider_model.name}: {e}")

    finally:
        # Save event log
        db.add(event_log)
        db.commit()


@router.post(
    "/webhook/git",
    summary="Receive Git Webhook",
    description="""
    Universal webhook receiver for GitLab, GitHub, and Bitbucket.

    **Platform Detection:**
    - Automatically detects the Git platform from webhook headers
    - GitLab: `X-Gitlab-Event` header
    - GitHub: `X-GitHub-Event` header
    - Bitbucket: `X-Event-Key` header

    **Supported Events:**
    - Push events (commits)
    - Merge/Pull requests
    - Issues
    - CI/CD pipelines
    - Comments
    - Tags and releases

    **Processing:**
    1. Parses incoming webhook payload
    2. Formats message based on provider type
    3. Sends notifications to all active providers in background
    4. Logs event to database for analytics

    **Configuration:**
    - Set this URL in your Git platform's webhook settings
    - Ensure you have at least one active provider configured
    """,
    responses={
        200: {
            "description": "Webhook successfully received and queued",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Webhook processed and queued for 2 provider(s)",
                        "event": {
                            "platform": "gitlab",
                            "type": "push",
                            "project": "myorg/myproject",
                            "author": "john.doe",
                        },
                        "providers": 2,
                    }
                }
            },
        },
        400: {
            "description": "Invalid webhook payload or unknown platform",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Unknown webhook platform. Check your headers."
                    }
                }
            },
        },
    },
)
async def receive_webhook(
    request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Receive and process webhooks from Git platforms."""
    try:
        # Get headers and body
        headers = dict(request.headers)
        try:
            payload = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        # Detect platform and get appropriate parser
        try:
            parser = get_parser(headers)
        except ValueError as e:
            logger.warning(f"Unknown webhook platform: {e}")
            raise HTTPException(status_code=400, detail=str(e))

        # Parse the event
        try:
            parsed_event = parser.parse(headers, payload)
        except ParserError as e:
            logger.error(f"Failed to parse webhook: {e}")
            raise HTTPException(status_code=400, detail=f"Parse error: {str(e)}")

        logger.info(
            f"Received {parsed_event.platform} {parsed_event.event_type} "
            f"event from {parsed_event.project}"
        )

        # Get all active providers
        active_providers = db.query(Provider).filter(Provider.active.is_(True)).all()

        if not active_providers:
            logger.warning("No active providers configured")
            return {
                "status": "accepted",
                "message": "Webhook received but no active providers",
                "event": {
                    "platform": parsed_event.platform,
                    "type": parsed_event.event_type,
                    "project": parsed_event.project,
                },
            }

        # Send to all active providers (in background)
        for provider in active_providers:
            background_tasks.add_task(process_and_send, parsed_event, provider, db)

        return {
            "status": "success",
            "message": f"Webhook processed and queued for {len(active_providers)} provider(s)",
            "event": {
                "platform": parsed_event.platform,
                "type": parsed_event.event_type,
                "project": parsed_event.project,
                "author": parsed_event.author,
            },
            "providers": len(active_providers),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/webhook/test",
    summary="Test Webhook Service",
    description="Simple test endpoint to verify that the webhook service is operational",
    responses={
        200: {
            "description": "Service is running",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok",
                        "message": "Webhook service is running",
                        "version": "1.0.0",
                    }
                }
            },
        }
    },
)
async def test_webhook() -> Dict[str, str]:
    """Test endpoint to verify webhook service is running."""
    return {"status": "ok", "message": "Webhook service is running", "version": "1.0.0"}
