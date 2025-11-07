"""Webhook model - stores webhook configurations (optional feature)"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Webhook(Base):
    """Webhook configuration (for multi-webhook support)"""

    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(100), unique=True, nullable=False, index=True)
    platform = Column(String(50), nullable=True)  # "gitlab", "github", or None for any
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Webhook(token='{self.token[:8]}...', platform='{self.platform}')>"
