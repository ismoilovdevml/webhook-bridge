"""Provider model - stores notification provider configurations"""

from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime
from sqlalchemy.sql import func
from app.database import Base
from typing import Dict, Any


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
    filters = Column(JSON, nullable=True)  # Event filtering rules
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Sensitive config fields by provider type
    SENSITIVE_FIELDS = {
        "telegram": ["bot_token"],
        "slack": ["webhook_url"],
        "discord": ["webhook_url"],
        "mattermost": ["webhook_url"],
        "email": ["smtp_password"],
    }

    def get_decrypted_config(self) -> Dict[str, Any]:
        """
        Get provider config with sensitive fields decrypted.

        Returns:
            Decrypted configuration dictionary
        """
        from app.utils.encryption import decrypt_field

        config = self.config.copy() if self.config else {}
        sensitive_fields = self.SENSITIVE_FIELDS.get(self.type, [])

        for field in sensitive_fields:
            if field in config and config[field]:
                try:
                    config[field] = decrypt_field(config[field])
                except Exception:
                    # If decryption fails, assume it's not encrypted (legacy data)
                    pass

        return config

    @staticmethod
    def encrypt_config(provider_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt sensitive fields in provider config.

        Args:
            provider_type: Type of provider (telegram, slack, etc.)
            config: Configuration dictionary

        Returns:
            Configuration with encrypted sensitive fields
        """
        from app.utils.encryption import encrypt_field

        encrypted_config = config.copy()
        sensitive_fields = Provider.SENSITIVE_FIELDS.get(provider_type, [])

        for field in sensitive_fields:
            if field in encrypted_config and encrypted_config[field]:
                encrypted_config[field] = encrypt_field(encrypted_config[field])

        return encrypted_config

    def should_notify(
        self, platform: str, event_type: str, project: str, branch: str = None
    ) -> bool:
        """
        Check if provider should be notified based on filters.

        Args:
            platform: Git platform (gitlab, github, bitbucket)
            event_type: Event type (push, merge_request, etc.)
            project: Project name (org/repo)
            branch: Branch name (optional)

        Returns:
            True if provider should be notified
        """
        # If no filters, notify for everything
        if not self.filters:
            return True

        filters = self.filters

        # Check platform filter
        if "platforms" in filters and filters["platforms"]:
            if platform not in filters["platforms"]:
                return False

        # Check event_type filter
        if "event_types" in filters and filters["event_types"]:
            if event_type not in filters["event_types"]:
                return False

        # Check project filter (supports wildcards)
        if "projects" in filters and filters["projects"]:
            import fnmatch

            project_match = False
            for pattern in filters["projects"]:
                if fnmatch.fnmatch(project, pattern):
                    project_match = True
                    break
            if not project_match:
                return False

        # Check branch filter
        if branch and "branches" in filters and filters["branches"]:
            if branch not in filters["branches"]:
                return False

        return True

    def __repr__(self):
        return (
            f"<Provider(name='{self.name}', type='{self.type}', active={self.active})>"
        )
