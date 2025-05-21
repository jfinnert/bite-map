import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add the app directory to the Python path
if os.path.exists('/app'):  # Running in Docker
    sys.path.insert(0, '/app')
else:  # Running locally
    # Assuming the script is run from the project root
    app_path = os.path.join(os.path.dirname(__file__), '../app')
    sys.path.insert(0, os.path.abspath(app_path))

try:
    from main import app
    # Create a test client
    client = TestClient(app)
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current sys.path: {sys.path}")
    raise

@pytest.fixture
def test_client():
    """Return a TestClient instance for testing FastAPI routes."""
    return client
