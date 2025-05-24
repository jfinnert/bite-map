import os
import sys

# Add the project root to the Python path AT THE VERY TOP
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

from typing import Generator, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from testcontainers.postgres import PostgresContainer

from app.main import app
from app.database import Base, get_db
from app.models import User, Place, Source, Review # Ensure all models are imported

@pytest.fixture(scope="session")
def engine():
    """Create a PostgreSQL test container with PostGIS for spatial testing."""
    with PostgresContainer("postgis/postgis:16-3.4") as pg:
        engine = create_engine(pg.get_connection_url(), future=True)
        print(f"Created test engine with PostgreSQL: {pg.get_connection_url()}")
        
        # Create all tables
        Base.metadata.create_all(engine)
        print("Tables created in PostgreSQL test container.")
        
        yield engine
        # Container auto-stops when context exits

@pytest.fixture(scope="function")
def test_db(engine) -> Generator[Session, Any, None]:
    """
    Provides a transactional scope for tests using PostgreSQL test container.
    Each test gets a fresh transaction that's rolled back after the test.
    """
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator[TestClient, Any, None]:
    """
    Provides a TestClient that uses the test_db session (PostgreSQL).
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            # The session is managed by the test_db fixture
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    # Clean up dependency override after test
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture(scope="function")
def mock_current_user(test_db: Session) -> User:
    """Create a mock user in the database for testing protected endpoints."""
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "hashed_password": "testpassword", # In a real app, hash the password
        "is_active": True,
        "is_superuser": False
    }
    
    user = User(**user_data)
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture(scope="function")
def auth_client(client: TestClient, mock_current_user: User) -> TestClient:
    """Authenticate the client using the mock user."""
    from app.core.auth import create_access_token # Local import
    token_data = {"sub": mock_current_user.username, "user_id": mock_current_user.id}
    access_token = create_access_token(data=token_data)
    client.headers["Authorization"] = f"Bearer {access_token}"
    return client
