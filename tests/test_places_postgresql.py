#!/usr/bin/env python3
"""
Simple test for places endpoint with PostgreSQL testcontainer
"""
import pytest
from factories import PlaceFactory
from geoalchemy2.shape import from_shape
from shapely.geometry import Point


@pytest.mark.timeout(120)  # 2 minutes timeout for container setup
def test_get_places_empty(client, test_db):
    """Test getting places when database is empty"""
    response = client.get("/api/places")
    assert response.status_code == 200
    
    data = response.json()
    assert "items" in data
    assert "meta" in data
    assert data["items"] == []
    assert data["meta"]["next"] is None


@pytest.mark.timeout(120)
def test_get_places_with_data(client, test_db):
    """Test getting places with some data"""
    # Create some test places using the factory
    PlaceFactory._meta.sqlalchemy_session = test_db
    
    # Create places in NYC
    place1 = PlaceFactory.create(
        name="Joe's Pizza",
        address="123 Broadway, New York, NY",
        geom=from_shape(Point(-73.935242, 40.730610), srid=4326)
    )
    place2 = PlaceFactory.create(
        name="Central Park Cafe", 
        address="456 Central Park West, New York, NY",
        geom=from_shape(Point(-73.958, 40.785), srid=4326)
    )
    
    test_db.commit()
    
    # Test the endpoint
    response = client.get("/api/places")
    assert response.status_code == 200
    
    data = response.json()
    assert "items" in data
    assert "meta" in data
    assert len(data["items"]) == 2
    
    # Check that coordinates are properly extracted
    for item in data["items"]:
        assert "lat" in item
        assert "lng" in item
        assert item["lat"] is not None
        assert item["lng"] is not None
        assert isinstance(item["lat"], float)
        assert isinstance(item["lng"], float)


@pytest.mark.timeout(120)
def test_get_places_bbox_filter(client, test_db):
    """Test bbox filtering"""
    PlaceFactory._meta.sqlalchemy_session = test_db
    
    # Create a place in NYC
    nyc_place = PlaceFactory.create(
        name="NYC Restaurant",
        geom=from_shape(Point(-73.935242, 40.730610), srid=4326)
    )
    
    # Create a place in SF
    sf_place = PlaceFactory.create(
        name="SF Restaurant", 
        geom=from_shape(Point(-122.419, 37.775), srid=4326)
    )
    
    test_db.commit()
    
    # Test NYC bbox filter (should only return NYC place)
    nyc_bbox = "-74.25909,40.477399,-73.700272,40.916178"
    response = client.get(f"/api/places?bbox={nyc_bbox}")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "NYC Restaurant"


@pytest.mark.timeout(120)  
def test_get_places_text_search(client, test_db):
    """Test text search functionality"""
    PlaceFactory._meta.sqlalchemy_session = test_db
    
    # Create places with different names
    pizza_place = PlaceFactory.create(
        name="Amazing Pizza Place",
        geom=from_shape(Point(-73.935242, 40.730610), srid=4326)
    )
    
    burger_place = PlaceFactory.create(
        name="Best Burger Joint",
        geom=from_shape(Point(-73.945, 40.740), srid=4326)
    )
    
    test_db.commit()
    
    # Test search for "pizza"
    response = client.get("/api/places?q=pizza")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["items"]) == 1
    assert "pizza" in data["items"][0]["name"].lower()
