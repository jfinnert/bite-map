# filepath: /Users/josh/Python/3.7/Bite Map Project/bite-map/tests/conftest.py
import os
import sys
import pytest
from unittest import mock
from fastapi.testclient import TestClient

# Add correct paths to Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_dir = os.path.join(project_dir, 'app')
sys.path.insert(0, project_dir)
sys.path.insert(0, app_dir)

# Import app - we do this here so the path setup happens first
from main import app

# Create a test client
test_client = TestClient(app)

@pytest.fixture
def client():
    """Return the test client."""
    return test_client
