"""Event logs API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..models.event import Event
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/events")


class EventResponse(BaseModel):
    """Event response schema."""
    id: int
    platform: str
    event_type: str
    project: str
    author: str
    branch: str | None
    provider_id: int
    status: str
    error_message: str | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=List[EventResponse])
def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    platform: str | None = None,
    event_type: str | None = None,
    status: str | None = None,
    project: str | None = None,
    db: Session = Depends(get_db)
) -> List[Event]:
    """
    Get list of events with optional filters.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return (max 100)
        platform: Filter by platform (gitlab, github, bitbucket)
        event_type: Filter by event type (push, merge_request, etc)
        status: Filter by status (success, failed, pending)
        project: Filter by project name
        db: Database session

    Returns:
        List of events
    """
    query = db.query(Event)

    # Apply filters
    if platform:
        query = query.filter(Event.platform == platform)
    if event_type:
        query = query.filter(Event.event_type == event_type)
    if status:
        query = query.filter(Event.status == status)
    if project:
        query = query.filter(Event.project.contains(project))

    # Order by most recent first
    events = query.order_by(desc(Event.created_at)).offset(skip).limit(limit).all()

    return events


@router.get("/stats")
def get_event_stats(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get event statistics.

    Args:
        db: Database session

    Returns:
        Event statistics
    """
    total_events = db.query(func.count(Event.id)).scalar()
    success_count = db.query(func.count(Event.id)).filter(Event.status == "success").scalar()
    failed_count = db.query(func.count(Event.id)).filter(Event.status == "failed").scalar()

    # Events by platform
    platform_stats = db.query(
        Event.platform,
        func.count(Event.id).label("count")
    ).group_by(Event.platform).all()

    # Events by type
    type_stats = db.query(
        Event.event_type,
        func.count(Event.id).label("count")
    ).group_by(Event.event_type).order_by(desc("count")).limit(10).all()

    # Recent activity (last 24 hours)
    from datetime import timedelta
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_count = db.query(func.count(Event.id)).filter(
        Event.created_at >= yesterday
    ).scalar()

    success_rate = (success_count / total_events * 100) if total_events > 0 else 0

    return {
        "total_events": total_events,
        "success_count": success_count,
        "failed_count": failed_count,
        "success_rate": round(success_rate, 2),
        "recent_24h": recent_count,
        "by_platform": {item.platform: item.count for item in platform_stats},
        "by_type": {item.event_type: item.count for item in type_stats},
    }


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db)
) -> Event:
    """
    Get event by ID.

    Args:
        event_id: Event ID
        db: Database session

    Returns:
        Event details
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Delete an event log.

    Args:
        event_id: Event ID
        db: Database session

    Returns:
        Success message
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Event not found")

    db.delete(event)
    db.commit()

    logger.info(f"Deleted event: {event_id}")
    return {"status": "success", "message": f"Event {event_id} deleted"}


@router.delete("")
def clear_events(
    status: str | None = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Clear event logs (optionally filtered by status).

    Args:
        status: Optional status filter (success, failed, pending)
        db: Database session

    Returns:
        Number of deleted events
    """
    query = db.query(Event)

    if status:
        query = query.filter(Event.status == status)

    count = query.count()
    query.delete()
    db.commit()

    logger.info(f"Cleared {count} events" + (f" with status '{status}'" if status else ""))
    return {
        "status": "success",
        "message": f"Cleared {count} event(s)",
        "count": count
    }
