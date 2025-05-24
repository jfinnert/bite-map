import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os
import sys
import tempfile

# Add project paths
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_dir = os.path.join(project_dir, 'app')
sys.path.insert(0, project_dir)
sys.path.insert(0, app_dir)

from app.database import Base, get_db
from app.main import app
from app import models  # Import models to ensure they're registered


@pytest.fixture(scope="session")
def postgres_container():
    """Start a PostgreSQL container with PostGIS extension for the test session."""
    with PostgresContainer(
        image="postgis/postgis:16-3.4",
        driver="psycopg2",
        username="test",
        password="test",
        dbname="testdb"
    ) as postgres:
        yield postgres


@pytest.fixture(scope="session")
def engine(postgres_container):
    """Create a database engine connected to the test PostgreSQL container."""
    connection_url = postgres_container.get_connection_url()
    engine = create_engine(connection_url, echo=False)
    
    # Create tables directly using SQLAlchemy instead of Alembic migrations
    # This avoids conflicts with model imports in Alembic env.py
    with engine.connect() as conn:
        # Enable PostGIS extension
        from sqlalchemy import text
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        conn.commit()
    
    # Create all tables
    Base.metadata.create_all(engine)
    
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(engine):
    """Create a database session for each test function."""
    connection = engine.connect()
    transaction = connection.begin()
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionLocal()
    
    # Override the get_db dependency
    def override_get_db():
        try:
            yield session
        finally:
            pass  # Don't close here, we'll handle it in cleanup
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield session
    
    # Cleanup
    session.close()
    transaction.rollback()
    connection.close()
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client for the FastAPI application."""
    return TestClient(app)