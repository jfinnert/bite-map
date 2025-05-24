#!/bin/bash
# filepath: /Users/josh/Python/3.7/Bite Map Project/bite-map/update_tests.sh
# Script to update tests for Bite Map project
# This script fixes common issues in tests and ensures they're handled cleanly

# Set variables
PROJECT_DIR="/Users/josh/Python/3.7/Bite Map Project/bite-map"
TESTS_DIR="${PROJECT_DIR}/tests"

echo "Updating tests in ${TESTS_DIR}..."

# 1. Fix duplicate file path comments
echo "Fixing duplicate file path comments..."
find "$TESTS_DIR" -type f -name "*.py" | xargs -I {} sed -i '' '/# filepath: /{
    n
    /# filepath: /d
}' {}

# 1a. Remove duplicate filepath comments in this script too
sed -i '' '1s/^# filepath.*\n//' "$0"

# 2. Make sure required test packages are available
echo "Checking for required test packages..."
# Use pip3 command if pip fails
PIP_CMD="pip"
if ! command -v pip &> /dev/null; then
    PIP_CMD="pip3"
fi

# Install all required dependencies from test-requirements.txt
if [ -f "${PROJECT_DIR}/test-requirements.txt" ]; then
    echo "Installing all test dependencies from test-requirements.txt..."
    $PIP_CMD install -r "${PROJECT_DIR}/test-requirements.txt"
    if [ $? -ne 0 ]; then
        echo "WARNING: Some dependencies couldn't be installed. Trying individual installs..."
        # Fall back to individual installs if the requirements file fails
        $PIP_CMD install pytest pytest-mock pytest-cov httpx fastapi sqlalchemy python-slugify || true
        $PIP_CMD install python-jose python-multipart passlib pydantic || true
        $PIP_CMD install psycopg2-binary || echo "Using SQLite for tests instead"
    fi
else
    echo "WARNING: test-requirements.txt not found. Installing minimal dependencies..."
    # Install pytest-mock if needed
    if ! $PIP_CMD list | grep -i -q "pytest[-_]mock"; then
        echo "Installing pytest-mock..."
        $PIP_CMD install pytest-mock==3.10.0
    fi

    # Install httpx for FastAPI testing
    if ! $PIP_CMD list | grep -i -q "httpx"; then
        echo "Installing httpx for FastAPI testing..."
        $PIP_CMD install httpx
    fi

    # Install python-slugify for tests needing it
    if ! $PIP_CMD list | grep -i -q "python[-_]slugify"; then
        echo "Installing python-slugify for tests..."
        $PIP_CMD install python-slugify==8.0.4
    fi

    # Install SQLAlchemy for database tests
    if ! $PIP_CMD list | grep -i -q "sqlalchemy"; then
        echo "Installing SQLAlchemy for database testing..."
        $PIP_CMD install SQLAlchemy
    fi

    # Install FastAPI
    if ! $PIP_CMD list | grep -i -q "fastapi"; then
        echo "Installing FastAPI for API testing..."
        $PIP_CMD install fastapi
    fi

    # Install authentication packages
    if ! $PIP_CMD list | grep -i -q "python[-_]jose"; then
        echo "Installing python-jose for authentication tests..."
        $PIP_CMD install python-jose
    fi

    if ! $PIP_CMD list | grep -i -q "passlib"; then
        echo "Installing passlib for password hashing in tests..."
        $PIP_CMD install passlib
    fi
    
    if ! $PIP_CMD list | grep -i -q "python[-_]multipart"; then
        echo "Installing python-multipart for form data handling..."
        $PIP_CMD install python-multipart
    fi

    # Install psycopg2 for PostgreSQL support
    if ! $PIP_CMD list | grep -i -q "psycopg2"; then
        echo "Installing psycopg2 for PostgreSQL support..."
        # Try psycopg2-binary if plain psycopg2 doesn't work
        $PIP_CMD install psycopg2-binary || echo "Using SQLite for tests instead"
    fi
fi  # End of test-requirements.txt condition

# 3. Fix import statements to use consistent path
echo "Fixing import statements..."
find "$TESTS_DIR" -type f -name "*.py" | xargs -I {} sed -i '' 's/from app\./from /g' {}

# 3a. Add import fixing function for handling both import styles
cat > "$TESTS_DIR/import_helper.py" << 'EOF'
# filepath: /Users/josh/Python/3.7/Bite Map Project/bite-map/tests/import_helper.py
"""Helper utility to handle imports in tests regardless of how the project is structured."""

import importlib.util
import sys
from functools import wraps

def flexible_import(module_name):
    """Try to import a module from either direct path or app.* path."""
    try:
        return __import__(module_name)
    except ImportError:
        try:
            return __import__(f"app.{module_name}")
        except ImportError:
            print(f"WARNING: Could not import {module_name} or app.{module_name}")
            return None

def get_module(name):
    """Get a module by name, trying different import paths."""
    # First try direct import
    try:
        return importlib.import_module(name)
    except ImportError:
        # Then try with app. prefix
        try:
            return importlib.import_module(f"app.{name}")
        except ImportError:
            return None
EOF

# 4. Manage app/tests directory
echo "Checking for app/tests directory..."
if [ -d "${PROJECT_DIR}/app/tests" ]; then
    echo "Found duplicate tests directory."
    # Check if there are any files in the tests directory that we should preserve
    if [ "$(ls -A "${PROJECT_DIR}/app/tests" 2>/dev/null)" ]; then
        echo "Creating a backup of app/tests before removing..."
        BACKUP_DIR="${PROJECT_DIR}/app/tests_backup_$(date +%Y%m%d)"
        mkdir -p "$BACKUP_DIR"
        
        # Copy files, ignoring errors if no files exist
        cp -r "${PROJECT_DIR}/app/tests"/* "$BACKUP_DIR/" 2>/dev/null || true
        echo "Backup created at: $BACKUP_DIR"
    else
        echo "app/tests directory appears to be empty or inaccessible."
    fi

    # Remove the directory if we have write permissions
    if [ -w "${PROJECT_DIR}/app" ]; then
        echo "Removing app/tests directory..."
        rm -rf "${PROJECT_DIR}/app/tests" 2>/dev/null || echo "Warning: Could not remove app/tests directory"
    fi
    
    echo "All tests are now consolidated in: ${PROJECT_DIR}/tests"
else
    echo "app/tests directory does not exist. All tests are already in the correct location."
fi

# 4a. Update conftest.py if it has duplicate comments or outdated imports
if grep -q "filepath.*filepath" "$TESTS_DIR/conftest.py"; then
    echo "Fixing conftest.py with duplicate file path comments..."
    sed -i '' '/# filepath: /{
        n
        /# filepath: /d
    }' "$TESTS_DIR/conftest.py"
fi

# 4b. Add proper import handling to conftest.py
cat > "$TESTS_DIR/conftest.py.new" << 'EOF'
# filepath: /Users/josh/Python/3.7/Bite Map Project/bite-map/tests/conftest.py
import os
import sys
import pytest
from unittest import mock

# Add correct paths to Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_dir = os.path.join(project_dir, 'app')
sys.path.insert(0, project_dir)
sys.path.insert(0, app_dir)

# Import FastAPI TestClient with error handling
try:
    from fastapi.testclient import TestClient
    has_fastapi = True
except ImportError:
    has_fastapi = False
    print("WARNING: FastAPI not installed. Some tests may fail.")
    # Create stub class for TestClient
    class TestClient:
        def __init__(self, app):
            self.app = app

# Import SQLAlchemy with error handling
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    has_sqlalchemy = True
except ImportError:
    has_sqlalchemy = False
    print("WARNING: SQLAlchemy not installed. Database tests will be skipped.")

# Create test database connection
if has_sqlalchemy:
    # Patch the database connection for testing
    import os
    # Set test database URL
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# Import app
try:
    from app.main import app
except ImportError:
    try:
        from main import app
    except ImportError:
        print("WARNING: Could not import app")
        # Create a stub app
        try:
            from fastapi import FastAPI
            app = FastAPI()
        except ImportError:
            # Create minimal app stub if FastAPI is not available
            app = object()

# Create a test client if FastAPI is available
if has_fastapi:
    test_client = TestClient(app)
else:
    test_client = None

@pytest.fixture
def client():
    """Return the test client."""
    if test_client is None:
        pytest.skip("FastAPI TestClient not available")
    return test_client

# Add database fixtures if SQLAlchemy is available
if has_sqlalchemy:
    # Import database components with error handling
    try:
        from app.database import Base, get_db
        has_db = True
    except ImportError:
        try:
            from database import Base, get_db
            has_db = True
        except ImportError:
            has_db = False
            print("WARNING: Could not import database components")
            # Create stub classes
            class Base:
                metadata = None
            def get_db():
                pass
    
    @pytest.fixture
    def test_db_engine():
        """Create a SQLite in-memory database engine for testing."""
        if not has_sqlalchemy or not has_db:
            pytest.skip("SQLAlchemy or database components not available")
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
    def client_with_db(test_db_session):
        """Return a test client with database dependency overridden."""
        if not has_fastapi:
            pytest.skip("FastAPI not available")
            
        def override_get_db():
            try:
                yield test_db_session
            finally:
                pass
        
        app.dependency_overrides[get_db] = override_get_db
        yield test_client
        app.dependency_overrides.clear()
EOF

# Only replace if import section is different
if ! grep -q "try:" "$TESTS_DIR/conftest.py"; then
    echo "Updating conftest.py with improved import handling..."
    mv "$TESTS_DIR/conftest.py.new" "$TESTS_DIR/conftest.py"
else
    rm "$TESTS_DIR/conftest.py.new"
fi

# 5. Check for skipped tests
echo "Checking for skipped tests..."
SKIPPED_TESTS=$(grep -r "@pytest.mark.skip" "$TESTS_DIR" | wc -l)
if [ "$SKIPPED_TESTS" -gt 0 ]; then
    echo "Found $SKIPPED_TESTS skipped tests. Consider implementing these tests with proper mocks."
    echo "Skipped tests:"
    grep -r "@pytest.mark.skip" "$TESTS_DIR" --include="*.py" -A 1
fi

# 6. Make sure we have the right database fixture
if [ ! -f "$TESTS_DIR/db_fixtures.py" ]; then
    echo "Creating database fixture file for testing..."
    cat > "$TESTS_DIR/db_fixtures.py" << 'EOF'
# filepath: /Users/josh/Python/3.7/Bite Map Project/bite-map/tests/db_fixtures.py
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import database components - we'll try both paths
try:
    from app.database import Base, get_db
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
EOF
fi

# 7. Check for common test issues and generate test report
echo "Checking for common test issues..."

TEST_REPORT="$PROJECT_DIR/test_report.md"
cat > "$TEST_REPORT" << EOF
# Bite Map Test Report
Generated: $(date)

## Test Coverage Summary

EOF

# Handle paths with spaces correctly
# Count total tests
TOTAL_TESTS=$(find "$TESTS_DIR" -type f -name "*.py" -exec grep -l "def test_" {} \; | wc -l)
SKIPPED_TESTS=$(find "$TESTS_DIR" -type f -name "*.py" -exec grep -l "@pytest.mark.skip" {} \; | wc -l)
IMPLEMENTED_TESTS=$((TOTAL_TESTS - SKIPPED_TESTS))

echo "Total tests found: $TOTAL_TESTS" >> "$TEST_REPORT"
echo "Implemented tests: $IMPLEMENTED_TESTS" >> "$TEST_REPORT"
echo "Skipped tests: $SKIPPED_TESTS" >> "$TEST_REPORT"
echo "" >> "$TEST_REPORT"
echo "## Test Files" >> "$TEST_REPORT"

# List all test files and their test counts
find "$TESTS_DIR" -name "test_*.py" | while read -r TEST_FILE; do
    FILE_NAME=$(basename "$TEST_FILE")
    FILE_TESTS=$(grep -c "def test_" "$TEST_FILE" || echo "0")
    FILE_SKIPPED=$(grep -c "@pytest.mark.skip" "$TEST_FILE" || echo "0")
    echo "- $FILE_NAME: $FILE_TESTS tests ($FILE_SKIPPED skipped)" >> "$TEST_REPORT"
done

echo "" >> "$TEST_REPORT"
echo "## Recommendations" >> "$TEST_REPORT"

# Add recommendations based on findings
if [ "$SKIPPED_TESTS" -gt 0 ]; then
    echo "- Implement the $SKIPPED_TESTS skipped tests using proper mocks" >> "$TEST_REPORT"
fi

echo "- Use the new db_fixtures.py to test database interactions" >> "$TEST_REPORT"
echo "- Consider adding more API tests for complete coverage" >> "$TEST_REPORT"

echo "Test report generated: $TEST_REPORT"

# 8. Run tests to check for errors
echo "Running tests to check for errors..."
cd "$PROJECT_DIR"
# Try different Python commands since 'python' wasn't found
if command -v python3 &> /dev/null; then
    echo "Running tests with python3..."
    python3 -m pytest -v tests/test_worker.py || echo "Some tests failed, but continuing with cleanup"
elif command -v python &> /dev/null; then
    echo "Running tests with python..."
    python -m pytest -v tests/test_worker.py || echo "Some tests failed, but continuing with cleanup"
else
    echo "Python command not found. Skipping test execution."
    echo "Please run tests manually with: python3 -m pytest tests/"
fi

echo "Test update complete!"
echo "Now run 'python3 -m pytest tests/' to verify all tests."