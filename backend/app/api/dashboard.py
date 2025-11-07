"""Dashboard API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Dict, Any, List
from datetime import datetime, timedelta

from ..database import get_db
from ..models.provider import Provider
from ..models.event import Event
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/dashboard")


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get dashboard statistics.

    Args:
        db: Database session

    Returns:
        Dashboard statistics including providers, events, and trends
    """
    # Provider stats
    total_providers = db.query(func.count(Provider.id)).scalar()
    active_providers = (
        db.query(func.count(Provider.id)).filter(Provider.active.is_(True)).scalar()
    )

    # Event stats
    total_events = db.query(func.count(Event.id)).scalar()
    success_events = (
        db.query(func.count(Event.id)).filter(Event.status == "success").scalar()
    )
    failed_events = (
        db.query(func.count(Event.id)).filter(Event.status == "failed").scalar()
    )

    # Calculate success rate
    success_rate = (success_events / total_events * 100) if total_events > 0 else 0

    # Time-based stats
    now = datetime.utcnow()
    last_24h = now - timedelta(days=1)
    last_7d = now - timedelta(days=7)
    last_30d = now - timedelta(days=30)

    events_24h = (
        db.query(func.count(Event.id)).filter(Event.created_at >= last_24h).scalar()
    )

    events_7d = (
        db.query(func.count(Event.id)).filter(Event.created_at >= last_7d).scalar()
    )

    events_30d = (
        db.query(func.count(Event.id)).filter(Event.created_at >= last_30d).scalar()
    )

    # Platform distribution
    platform_stats = (
        db.query(Event.platform, func.count(Event.id).label("count"))
        .group_by(Event.platform)
        .all()
    )

    # Event type distribution (top 10)
    type_stats = (
        db.query(Event.event_type, func.count(Event.id).label("count"))
        .group_by(Event.event_type)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )

    # Provider distribution
    provider_stats = (
        db.query(Provider.name, func.count(Event.id).label("event_count"))
        .join(Event, Provider.id == Event.provider_id)
        .group_by(Provider.name)
        .order_by(desc("event_count"))
        .all()
    )

    return {
        "providers": {
            "total": total_providers,
            "active": active_providers,
            "inactive": total_providers - active_providers,
        },
        "events": {
            "total": total_events,
            "success": success_events,
            "failed": failed_events,
            "success_rate": round(success_rate, 2),
            "last_24h": events_24h,
            "last_7d": events_7d,
            "last_30d": events_30d,
        },
        "distribution": {
            "by_platform": {item.platform: item.count for item in platform_stats},
            "by_type": {item.event_type: item.count for item in type_stats},
            "by_provider": {item.name: item.event_count for item in provider_stats},
        },
    }


@router.get("/recent-events")
def get_recent_events(
    limit: int = 10, db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get recent events for dashboard display.

    Args:
        limit: Number of recent events to return (default 10)
        db: Database session

    Returns:
        List of recent events with provider info
    """
    events = (
        db.query(Event)
        .join(Provider, Event.provider_id == Provider.id)
        .order_by(desc(Event.created_at))
        .limit(limit)
        .all()
    )

    result = []
    for event in events:
        provider = db.query(Provider).filter(Provider.id == event.provider_id).first()
        result.append(
            {
                "id": event.id,
                "platform": event.platform,
                "event_type": event.event_type,
                "project": event.project,
                "author": event.author,
                "status": event.status,
                "provider_name": provider.name if provider else "Unknown",
                "provider_type": provider.type if provider else "Unknown",
                "created_at": event.created_at.isoformat(),
            }
        )

    return result


@router.get("/activity-timeline")
def get_activity_timeline(
    days: int = 7, db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get activity timeline for the last N days.

    Args:
        days: Number of days to include (default 7)
        db: Database session

    Returns:
        Daily activity counts
    """
    start_date = datetime.utcnow() - timedelta(days=days)

    # Query events grouped by date
    daily_stats = (
        db.query(
            func.date(Event.created_at).label("date"),
            func.count(Event.id).label("total"),
            func.sum(func.case((Event.status == "success", 1), else_=0)).label(
                "success"
            ),
            func.sum(func.case((Event.status == "failed", 1), else_=0)).label("failed"),
        )
        .filter(Event.created_at >= start_date)
        .group_by(func.date(Event.created_at))
        .order_by("date")
        .all()
    )

    result = []
    for stat in daily_stats:
        result.append(
            {
                "date": stat.date.isoformat() if stat.date else None,
                "total": stat.total or 0,
                "success": stat.success or 0,
                "failed": stat.failed or 0,
            }
        )

    return result


@router.get("/health")
def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring.

    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "service": "webhook-bridge",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }
