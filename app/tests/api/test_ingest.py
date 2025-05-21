import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import json
from unittest import mock

# Import the test client from conftest
from conftest import client


def test_health_endpoint():
    """Test the health check endpoint returns status ok."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ingest_endpoint():
    """Test the link ingestion endpoint."""
    # Mock URL to test
    test_url = "https://www.youtube.com/watch?v=test123"
    
    # Mock request data
    request_data = {
        "url": test_url
    }
    
    # Mock the database session to avoid actual DB operations
    with mock.patch("app.api.endpoints.ingest.get_db") as mock_get_db:
        # Mock the session and query methods
        mock_session = mock.MagicMock()
        mock_get_db.return_value = mock_session
        
        # Configure the mock session to handle the source creation
        mock_source = mock.MagicMock()
        mock_source.id = 1
        mock_source.url = test_url
        mock_source.platform = "youtube"
        
        # Set up the session to return our mock source after db.add() is called
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.side_effect = lambda x: setattr(x, 'id', 1)
        
        # Also mock the background tasks
        with mock.patch("app.api.endpoints.ingest.BackgroundTasks") as mock_bg_tasks:
            response = client.post(
                "/api/ingest/link",
                json=request_data
            )
            
            # Check response
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["status"] == "success"
            assert response_data["url"] == test_url
            assert response_data["platform"] == "youtube"
            
            # Verify that the source was added and committed
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
