"""Main FastAPI application for Webhook Bridge."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import init_db
from .api import api_router
from .utils.logger import setup_logging, get_logger

# Setup logging
setup_logging(level=settings.LOG_LEVEL)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Webhook Bridge application...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database: {settings.DATABASE_URL}")

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Webhook Bridge application...")


# Create FastAPI app
app = FastAPI(
    title="Webhook Bridge API",
    description=(
        "Universal webhook receiver for GitLab, GitHub, and Bitbucket. "
        "Forward Git events to Telegram, Slack, Discord, Mattermost, and Email."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "health", "description": "Health check and system status"},
        {"name": "webhooks", "description": "Webhook receiver for Git platforms"},
        {"name": "providers", "description": "Notification providers management"},
        {"name": "events", "description": "Webhook events history"},
        {"name": "dashboard", "description": "Statistics and analytics"},
    ],
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


@app.get(
    "/",
    tags=["health"],
    summary="Root endpoint",
    description="Get basic information about the Webhook Bridge API",
)
def root():
    """Root endpoint with API information."""
    return {
        "service": "Webhook Bridge API",
        "version": "1.0.0",
        "status": "running",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        },
        "endpoints": {
            "health": "/health",
            "webhook": "/api/webhook/git",
            "providers": "/api/providers",
            "events": "/api/events",
            "dashboard": "/api/dashboard",
        },
    }


@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Check if the service is healthy and running",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "service": "webhook-bridge",
                        "version": "1.0.0",
                    }
                }
            },
        }
    },
)
def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {"status": "healthy", "service": "webhook-bridge", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )
