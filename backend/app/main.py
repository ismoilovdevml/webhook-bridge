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
    title="Webhook Bridge",
    description="Universal Git Notification System - Forward webhooks from GitLab, GitHub, Bitbucket to any notification platform",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
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


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "service": "Webhook Bridge",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs" if settings.ENVIRONMENT == "development" else "disabled",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "webhook-bridge",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower()
    )
