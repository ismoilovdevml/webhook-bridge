"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "sqlite:///./webhook_bridge.db"

    # Security
    SECRET_KEY: str = "change-this-in-production"
    WEBHOOK_SECRET: str = ""

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"

    # CORS
    CORS_ORIGINS_STR: str = "http://localhost:3000,http://localhost:5173"

    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",")]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "webhook_bridge.log"
    JSON_LOGS: bool = False

    # Features
    ENABLE_ANALYTICS: bool = True
    ENABLE_EVENT_LOGGING: bool = True
    MAX_EVENTS_PER_PAGE: int = 50

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


settings = Settings()
