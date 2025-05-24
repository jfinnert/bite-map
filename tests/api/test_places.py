import pytest
import os
import sys
from fastapi import status
from fastapi.testclient import TestClient
from unittest import mock
import json

# Add app to sys path if needed
project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
app_dir = os.path.join(project_dir, 'app')
sys.path.insert(0, project_dir)
sys.path.insert(0, app_dir)

# Import app and database components
try:
    from main import app
    from database import get_db
except ImportError:
    try:
        from main import app
        from database import get_db
    except ImportError:
        print("WARNING: Could not import app or database. Tests may fail.")

def get_test_client():
    """Get a fresh test client for each test"""
    return TestClient(app)

def test_get_places_basic():
    """Test the basic places endpoint functionality."""
    client = get_test_client()
    
    # Mock data for places
    mock_places = [
        {
            "id": 1,
            "name": "Joe's Pizza",
            "slug": "joes-pizza-new-york",
            "address": "123 Main St, New York, NY",
            "lat": 40.730610,
            "lng": -73.935242,
            "rating": 4.5,
            "review_count": 3,
            "created_at": "2025-05-20T12:00:00Z",
            "updated_at": "2025-05-20T12:00:00Z",
        },
        {
            "id": 2,
            "name": "Shake Shack",
            "slug": "shake-shack-manhattan",
            "address": "456 Broadway, New York, NY",
            "lat": 40.712742,
            "lng": -74.006058,
            "rating": 4.2,
            "review_count": 5,
            "created_at": "2025-05-19T12:00:00Z",
            "updated_at": "2025-05-19T12:00:00Z",
        }
    ]
    
    # Mock the database query for places
    with mock.patch("api.endpoints.places.get_places") as mock_get_places:
        mock_get_places.return_value = mock_places
        
        # Test the basic endpoint
        response = client.get("/api/places/")
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Joe's Pizza"
        assert data[1]["slug"] == "shake-shack-manhattan"


def test_get_place_by_slug():
    """Test retrieving a place by slug."""
    client = get_test_client()
    
    # Mock place data
    mock_place = {
        "id": 1,
        "name": "Joe's Pizza",
        "slug": "joes-pizza-new-york",
        "address": "123 Main St, New York, NY",
        "lat": 40.730610,
        "lng": -73.935242,
        "rating": 4.5,
        "review_count": 3,
        "created_at": "2025-05-20T12:00:00Z",
        "updated_at": "2025-05-20T12:00:00Z",
        "reviews": [
            {
                "id": 1,
                "text": "Great pizza!",
                "rating": 5,
                "source_id": 1,
                "created_at": "2025-05-20T12:00:00Z"
            }
        ]
    }
    
    # Mock the database query for single place
    with mock.patch("api.endpoints.places.get_place_by_slug") as mock_get_place:
        # First test - place found
        mock_get_place.return_value = mock_place
        
        response = client.get("/api/places/joes-pizza-new-york")
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Joe's Pizza"
        assert data["slug"] == "joes-pizza-new-york"
        assert len(data["reviews"]) == 1
        
        # Second test - place not found
        mock_get_place.return_value = None
        
        response = client.get("/api/places/nonexistent-place")
        assert response.status_code == status.HTTP_404_NOT_FOUND
