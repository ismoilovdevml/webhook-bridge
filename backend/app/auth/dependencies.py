"""Authentication dependencies for FastAPI."""

from typing import Optional
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.api_key import APIKey
from ..database import get_db
from ..config import settings


async def get_api_key(
    x_api_key: Optional[str] = Header(None, alias=settings.API_KEY_HEADER),
    db: Session = Depends(get_db),
) -> Optional[APIKey]:
    """
    Validate API key from request header.

    Args:
        x_api_key: API key from request header
        db: Database session

    Returns:
        APIKey object if valid, None if auth disabled

    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not settings.API_KEY_ENABLED:
        return None

    if not x_api_key:
        raise HTTPException(
            status_code=401, detail=f"Missing {settings.API_KEY_HEADER} header"
        )

    # Query database for API key
    api_key = db.query(APIKey).filter(APIKey.key == x_api_key).first()

    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if not api_key.is_active:
        raise HTTPException(status_code=401, detail="API key is disabled")

    # Update last used timestamp
    api_key.last_used_at = datetime.utcnow()
    db.commit()

    return api_key


async def require_api_key(
    api_key: Optional[APIKey] = Depends(get_api_key),
) -> Optional[APIKey]:
    """
    Require valid API key.

    Args:
        api_key: API key from get_api_key dependency

    Returns:
        APIKey object

    Raises:
        HTTPException: If API key is required but not provided
    """
    if settings.API_KEY_ENABLED and api_key is None:
        raise HTTPException(
            status_code=401, detail="API key required but not provided"
        )

    return api_key
