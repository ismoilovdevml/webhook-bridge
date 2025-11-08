"""Event model - stores event logs"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from app.database import Base


class Event(Base):
    """Event log entry"""

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(
        String(50), nullable=False, index=True
    )  # "gitlab", "github", "bitbucket"
    event_type = Column(
        String(50), nullable=False, index=True
    )  # "push", "merge_request", etc.
    project = Column(String(200), nullable=False, index=True)  # "edcom/edcom-server"
    author = Column(String(100))  # "fatxulla"
    branch = Column(String(200), nullable=True)  # "main", "develop", etc.
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    provider_name = Column(String(100))  # Denormalized for quick access
    status = Column(
        String(20), nullable=False, default="success"
    )  # "success", "failed", "skipped"
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Composite indexes for common query patterns
    __table_args__ = (
        Index("idx_platform_event_type", "platform", "event_type"),
        Index("idx_status_created_at", "status", "created_at"),
        Index("idx_project_created_at", "project", "created_at"),
        Index("idx_provider_status", "provider_id", "status"),
    )

    def __repr__(self):
        return (
            f"<Event(platform='{self.platform}', "
            f"type='{self.event_type}', project='{self.project}')>"
        )
