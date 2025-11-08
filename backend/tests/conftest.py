"""Pytest configuration and fixtures."""
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app

# Set test environment variables before importing app
os.environ["ENCRYPTION_KEY"] = "test_key_32_bytes_long_for_fernet_encryption_12345678"
os.environ["WEBHOOK_SECRET"] = "test_webhook_secret"
os.environ["API_KEY_ENABLED"] = "True"

# Import settings after setting environment
from app.config import settings

# Override settings for testing
settings.ENCRYPTION_KEY = "test_key_32_bytes_long_for_fernet_encryption_12345678"
settings.WEBHOOK_SECRET = "test_webhook_secret"
settings.API_KEY_ENABLED = True


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def override_get_db(db_session):
    """Override the get_db dependency with test database."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def setup_db(override_get_db):
    """Automatically setup database for all tests."""
    pass


@pytest.fixture
def client():
    """Test client fixture."""
    from fastapi.testclient import TestClient

    return TestClient(app)
