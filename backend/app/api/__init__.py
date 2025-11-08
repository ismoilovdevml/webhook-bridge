"""API routes for webhook bridge."""

from fastapi import APIRouter
from .auth import router as auth_router
from .webhooks import router as webhooks_router
from .providers import router as providers_router
from .events import router as events_router
from .dashboard import router as dashboard_router

# Create main API router
api_router = APIRouter(prefix="/api")

# Include sub-routers
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(webhooks_router, tags=["webhooks"])
api_router.include_router(providers_router, tags=["providers"])
api_router.include_router(events_router, tags=["events"])
api_router.include_router(dashboard_router, tags=["dashboard"])

__all__ = ["api_router"]
