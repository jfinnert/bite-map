# filepath: /Users/josh/Python/3.7/Bite Map Project/bite-map/tests/api/test_ingest.py
import pytest
from fastapi.testclient import TestClient
from unittest import mock

# Import app early to avoid import order issues
from main import app

def get_test_client():
    """Get a fresh test client for each test"""
    return TestClient(app)

def test_health_endpoint():
    """Test the health check endpoint returns status ok."""
    client = get_test_client()
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.skip(reason="Database connection required")
def test_ingest_endpoint():
    """Test the link ingestion endpoint."""
    # Skipped because it requires database access
    pass
