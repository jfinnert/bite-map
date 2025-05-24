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


import pytest
from tests.factories import PlaceFactory

@pytest.mark.timeout(1.0)  # More generous during development, tighten to 0.1s later
def test_bbox_filters_rows(test_db, client):
    # Seed 10 NYC, 10 SF, 5 global
    for _ in range(10):
        PlaceFactory.create_nyc(session=test_db)
        PlaceFactory.create_sf(session=test_db)
    for _ in range(5):
        PlaceFactory(global_random=True, session=test_db)
    test_db.commit()
    # NYC bbox
    bbox = "-74.25909,40.477399,-73.700272,40.916178"
    resp = client.get(f"/api/places?bbox={bbox}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) <= 20  # default per_page
    for place in data["items"]:
        assert -74.25909 <= place["lng"] <= -73.700272
        assert 40.477399 <= place["lat"] <= 40.916178

@pytest.mark.timeout(1.0)  # More generous during development, tighten to 0.1s later
def test_search_filters_rows(test_db, client):
    PlaceFactory(session=test_db, name="Joe's Pizza")
    PlaceFactory(session=test_db, name="Shake Shack")
    PlaceFactory(session=test_db, name="Burger King")
    test_db.commit()
    resp = client.get("/api/places?q=pizza")
    assert resp.status_code == 200
    data = resp.json()
    assert any("pizza" in p["name"].lower() for p in data["items"])
    assert all("pizza" in p["name"].lower() or "pizza" in p["slug"] for p in data["items"])

@pytest.mark.timeout(1.0)  # More generous during development, tighten to 0.1s later
def test_pagination_meta(test_db, client):
    # Seed 30 places
    for _ in range(30):
        PlaceFactory.create_nyc(session=test_db)
    test_db.commit()
    # First page
    resp1 = client.get("/api/places?per_page=20")
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert len(data1["items"]) == 20
    next_id = data1["meta"]["next"]
    # Second page
    resp2 = client.get(f"/api/places?per_page=20&after_id={next_id}")
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert len(data2["items"]) <= 10
    # No more pages
    assert data2["meta"]["next"] is None
