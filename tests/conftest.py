import os
import sys

# Add the project root to the Python path AT THE VERY TOP
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

from typing import Generator, Any
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.database import Base, get_db # get_engine is no longer used directly from here for test_engine
from app.models import User, Place, Source, Review # Ensure all models are imported

# Use an in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"
print(f"Conftest: Using TEST_DATABASE_URL: {TEST_DATABASE_URL}")

test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
print("Engine id used for create_all (SQLite in-memory):", id(test_engine))

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_db(request):
    """
    Set up the database for the test session.
    Creates all tables in the in-memory SQLite database.
    """
    print(f"Models in Base.metadata before create_all: {Base.metadata.tables.keys()}")
    Base.metadata.create_all(bind=test_engine)
    print("Tables created in in-memory SQLite database.")

    # No drop_all needed for in-memory that disappears after session,
    # but if we want to be explicit for potential future non-memory test DBs:
    # def teardown():
    #     Base.metadata.drop_all(bind=test_engine)
    #     print("Tables dropped.")
    # request.addfinalizer(teardown)


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, Any, None]:
    """
    Provides a transactional scope for tests using the in-memory SQLite database.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    print("Engine id used by Session (SQLite in-memory):", id(session.get_bind()))

    # For SQLite, nested transactions are typically emulated using savepoints by default.
    # Explicitly starting a savepoint for clarity if needed, but SQLAlchemy handles it.
    # nested = connection.begin_nested()

    # @event.listens_for(session, "after_transaction_end")
    # def end_savepoint(session, transaction):
    #     nonlocal nested
    #     if not nested.is_active: # Check if the savepoint is still active
    #         nested = connection.begin_nested()


    try:
        yield session
    finally:
        session.close()
        # Rollback the overall transaction
        transaction.rollback()
        connection.close()

@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator[TestClient, Any, None]: # Corrected return type
    """
    Provides a TestClient that uses the test_db session (SQLite in-memory).
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            # The session is managed by the test_db fixture (closed, rolled back)
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    # Clean up dependency override after test
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture(scope="function")
def mock_current_user(test_db: Session) -> User:
    # Create a mock user in the database for testing protected endpoints
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com", # Corrected email for mock user
        "hashed_password": "testpassword", # In a real app, hash the password
        "is_active": True,
        "is_superuser": False
    }
    print(f"mock_current_user: User class id: {id(User)}, Base.registry._class_registry: {User in Base.registry._class_registry}")
    db_user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=user_data["hashed_password"],
        is_active=user_data["is_active"],
        is_superuser=user_data["is_superuser"]
    )
    test_db.add(db_user)
    test_db.commit()
    test_db.refresh(db_user)
    return db_user

@pytest.fixture(scope="function")
def auth_client(client: TestClient, mock_current_user: User) -> TestClient:
    # Authenticate the client using the mock user
    from app.core.auth import create_access_token # Local import
    token_data = {"sub": mock_current_user.username, "user_id": mock_current_user.id}
    access_token = create_access_token(data=token_data)
    client.headers["Authorization"] = f"Bearer {access_token}"
    return client
