# filepath: /Users/josh/Python/3.7/Bite Map Project/bite-map/tests/db_fixtures.py
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import database components - we'll try both paths
try:
    from database import Base, get_db
except ImportError:
    try:
        from database import Base, get_db
    except ImportError:
        print("WARNING: Could not import database components")
        # Create stub classes to allow the file to be imported
        class Base:
            metadata = None
        def get_db():
            pass

@pytest.fixture
def test_db_engine():
    """Create a SQLite in-memory database engine for testing."""
    engine = create_engine("sqlite:///:memory:")
    if Base.metadata:
        Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture
def test_db_session(test_db_engine):
    """Create a new database session for testing."""
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def override_get_db(test_db_session):
    """Return a function that overrides the get_db dependency."""
    def _override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    return _override_get_db
