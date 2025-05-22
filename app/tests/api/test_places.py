import pytest
import json
from unittest import mock
from fastapi.testclient import TestClient
from geoalchemy2.elements import WKTElement

# Import the test client from conftest
from conftest import client


def test_get_places_basic():
    """Test the basic places endpoint functionality."""
    with mock.patch("api.endpoints.places.get_db") as mock_get_db:
        # Mock the database session
        mock_session = mock.MagicMock()
        mock_get_db.return_value = mock_session
        
        # Create mock places and configure the query
        mock_places = []
        for i in range(3):
            mock_place = mock.MagicMock()
            mock_place.id = i + 1
            mock_place.name = f"Test Place {i + 1}"
            mock_place.slug = f"test-place-{i + 1}"
            mock_place.address = f"123 Test St, City {i + 1}"
            mock_place.city = f"City {i + 1}"
            mock_place.state = "State"
            mock_place.country = "Country"
            mock_places.append(mock_place)
        
        # Set up the session query to return our mock places
        mock_query = mock_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_places
        mock_query.count.return_value = len(mock_places)
        
        # Mock the ST_AsGeoJSON function to return GeoJSON for each place
        mock_session.scalar.side_effect = lambda x: json.dumps({
            "type": "Point", 
            "coordinates": [-73.935242, 40.730610]
        })
        
        # Call the endpoint
        response = client.get("/api/places")
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        
        # Verify the structure of the response
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 3
        assert "metadata" in data
        assert data["metadata"]["total"] == 3
        assert data["metadata"]["limit"] == 50  # default
        
        # Check first feature
        feature = data["features"][0]
        assert feature["type"] == "Feature"
        assert feature["geometry"]["type"] == "Point"
        assert feature["properties"]["name"] == "Test Place 1"


def test_get_place_by_id():
    """Test getting a single place by ID."""
    with mock.patch("api.endpoints.places.get_db") as mock_get_db:
        # Mock the database session
        mock_session = mock.MagicMock()
        mock_get_db.return_value = mock_session
        
        # Create a mock place
        mock_place = mock.MagicMock()
        mock_place.id = 1
        mock_place.name = "Test Place"
        mock_place.slug = "test-place"
        mock_place.address = "123 Test St"
        mock_place.city = "Test City"
        mock_place.state = "Test State"
        mock_place.country = "Test Country"
        mock_place.reviews = []
        
        # Set up the session query to return our mock place
        mock_query = mock_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_place
        
        # Call the endpoint
        response = client.get("/api/places/1")
        
        # Check response
        assert response.status_code == 200
        
        # Test non-existent place
        mock_query.first.return_value = None
        response = client.get("/api/places/999")
        assert response.status_code == 404
