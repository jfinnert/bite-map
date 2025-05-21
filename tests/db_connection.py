import sys
import os
import pytest
from sqlalchemy import text

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import engine

def test_database_connection():
    """Test that we can connect to the database."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert result.scalar() == 1
            print("Database connection successful!")
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")

def test_tables_exist():
    """Test that the expected tables exist in the database."""
    expected_tables = ["sources", "places", "reviews"]
    try:
        with engine.connect() as connection:
            for table in expected_tables:
                result = connection.execute(
                    text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
                )
                assert result.scalar(), f"Table {table} does not exist"
            print("All expected tables exist!")
    except Exception as e:
        pytest.fail(f"Table check failed: {e}")

if __name__ == "__main__":
    test_database_connection()
    test_tables_exist()
