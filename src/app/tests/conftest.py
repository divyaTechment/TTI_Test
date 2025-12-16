"""
Pytest configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..database.base import Base, get_db
from ..main import app
from ..core.config import settings

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create test database session."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database override."""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Test user data for creating users."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "TestPassword123"
    }


@pytest.fixture
def test_user(db_session, test_user_data):
    """Create a test user."""
    from ..services.user import UserService
    
    user_service = UserService(db_session)
    user = user_service.create_user(test_user_data)
    return user


@pytest.fixture
def test_superuser_data():
    """Test superuser data."""
    return {
        "email": "admin@example.com",
        "username": "admin",
        "full_name": "Admin User",
        "password": "AdminPassword123",
        "is_superuser": True
    }


@pytest.fixture
def test_superuser(db_session, test_superuser_data):
    """Create a test superuser."""
    from ..services.user import UserService
    
    user_service = UserService(db_session)
    user = user_service.create_user(test_superuser_data)
    return user


@pytest.fixture
def auth_headers(client, test_user_data):
    """Get authentication headers for test user."""
    response = client.post("/api/v1/auth/login", json=test_user_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def superuser_headers(client, test_superuser_data):
    """Get authentication headers for test superuser."""
    response = client.post("/api/v1/auth/login", json=test_superuser_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
