"""Provider model - stores notification provider configurations"""

from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Provider(Base):
    """Notification provider configuration"""

    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # "Main Telegram", "DevOps Slack"
    type = Column(
        String(50), nullable=False
    )  # "telegram", "slack", "mattermost", "discord"
    active = Column(Boolean, default=True, nullable=False)
    config = Column(JSON, nullable=False)  # Provider-specific configuration
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return (
            f"<Provider(name='{self.name}', type='{self.type}', active={self.active})>"
        )
