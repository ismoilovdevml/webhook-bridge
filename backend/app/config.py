"""Application configuration"""

from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List, Self


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "sqlite:///./webhook_bridge.db"

    # Security
    SECRET_KEY: str = "change-this-in-production"
    WEBHOOK_SECRET: str = ""
    ENCRYPTION_KEY: str = ""  # For encrypting sensitive provider data

    # Admin User (Created on first startup)
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "change-this-password"
    ADMIN_EMAIL: str = "admin@localhost"

    @model_validator(mode='after')
    def validate_production_settings(self) -> Self:
        """Validate that production environment has secure settings."""
        if self.ENVIRONMENT == "production":
            issues = []

            # Check for default/weak SECRET_KEY
            if self.SECRET_KEY in ["change-this-in-production", "", None]:
                issues.append(
                    "SECRET_KEY is using default value! "
                    "Generate a strong key: "
                    "python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )

            # Check for default ADMIN_PASSWORD
            if self.ADMIN_PASSWORD in ["change-this-password", "admin", ""]:
                issues.append(
                    "ADMIN_PASSWORD is using default/weak value! Set a strong password."
                )

            # Check SECRET_KEY strength
            if len(self.SECRET_KEY) < 32:
                issues.append(
                    f"SECRET_KEY is too short ({len(self.SECRET_KEY)} chars). "
                    "Use at least 32 characters."
                )

            # Warn if ENCRYPTION_KEY not set (it will be auto-generated with warning)
            if not self.ENCRYPTION_KEY:
                issues.append(
                    "ENCRYPTION_KEY not set! It will be auto-generated but lost on restart."
                )

            if issues:
                error_msg = (
                    "\n" + "=" * 70 + "\n"
                    "🔴 CRITICAL SECURITY WARNINGS IN PRODUCTION:\n\n"
                    + "\n".join(f"  {i + 1}. {issue}"
                                for i, issue in enumerate(issues))
                    + "\n" + "=" * 70 + "\n"
                )
                # In production, these should be errors, not just warnings
                raise ValueError(error_msg)

        return self

    # API Authentication
    API_KEY_ENABLED: bool = True
    API_KEY_HEADER: str = "X-API-Key"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"

    # CORS
    CORS_ORIGINS_STR: str = "http://localhost:3000,http://localhost:5173"

    @property
    def CORS_ORIGINS(self) -> List[str]:
        origins = [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",")]
        # Security: Prevent wildcard when credentials are enabled
        if "*" in origins and self.ENVIRONMENT == "production":
            raise ValueError(
                "CORS wildcard (*) not allowed in production. "
                "Set CORS_ORIGINS_STR to specific domains."
            )
        return origins

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "webhook_bridge.log"
    JSON_LOGS: bool = False

    # Features
    ENABLE_ANALYTICS: bool = True
    ENABLE_EVENT_LOGGING: bool = True
    MAX_EVENTS_PER_PAGE: int = 50

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 100

    # Retry Logic
    RETRY_ENABLED: bool = True
    RETRY_MAX_ATTEMPTS: int = 3
    RETRY_INITIAL_DELAY: float = 1.0  # seconds
    RETRY_MAX_DELAY: float = 60.0  # seconds
    RETRY_EXPONENTIAL_BASE: float = 2.0

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


settings = Settings()
