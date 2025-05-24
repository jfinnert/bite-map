#!/usr/bin/env python3
"""
Tests for the place detail endpoint (GET /api/places/{id})
"""
import pytest
from tests.factories import PlaceFactory, UserFactory
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from app.models import Review


@pytest.mark.timeout(120)
def test_get_place_detail_not_found(client, test_db):
    """Test getting a place that doesn't exist"""
    response = client.get("/api/places/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Place not found"


@pytest.mark.timeout(120)
def test_get_place_detail_basic(client, test_db):
    """Test getting basic place details without reviews"""
    PlaceFactory._meta.sqlalchemy_session = test_db
    
    # Create a place
    place = PlaceFactory.create(
        name="Joe's Pizza",
        address="123 Broadway, New York, NY",
        geom=from_shape(Point(-73.935242, 40.730610), srid=4326)
    )
    test_db.commit()
    
    # Test the endpoint
    response = client.get(f"/api/places/{place.id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == place.id
    assert data["name"] == "Joe's Pizza"
    assert data["address"] == "123 Broadway, New York, NY"
    assert data["lat"] == pytest.approx(40.730610, abs=1e-5)
    assert data["lng"] == pytest.approx(-73.935242, abs=1e-5)
    assert data["reviews"] == []


@pytest.mark.timeout(120)
def test_get_place_detail_with_reviews(client, test_db):
    """Test getting place details with reviews and source URLs"""
    PlaceFactory._meta.sqlalchemy_session = test_db
    UserFactory._meta.sqlalchemy_session = test_db
    
    # Create two different users for the reviews
    user1 = UserFactory.create(username="user1", email="user1@example.com")
    user2 = UserFactory.create(username="user2", email="user2@example.com")
    test_db.commit()
    
    # Create a place
    place = PlaceFactory.create(
        name="Amazing Restaurant",
        address="456 Main St, San Francisco, CA",
        geom=from_shape(Point(-122.419, 37.775), srid=4326)
    )
    test_db.commit()
    
    # Create some reviews with source URLs and thumbnails
    review1 = Review(
        rating=5,
        comment="Excellent food and service! Best place in the city.",
        source_url="https://yelp.com/review/123",
        thumbnail_url="https://images.yelp.com/thumb1.jpg",
        user_id=user1.id,
        place_id=place.id
    )
    
    review2 = Review(
        rating=4,
        comment="Good pizza, nice atmosphere",
        source_url="https://google.com/review/456",
        thumbnail_url=None,  # No thumbnail
        user_id=user2.id,  # Different user
        place_id=place.id
    )
    
    test_db.add(review1)
    test_db.add(review2)
    test_db.commit()
     # Test the endpoint
    response = client.get(f"/api/places/{place.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == place.id
    assert data["name"] == "Amazing Restaurant"
    assert len(data["reviews"]) == 2

    # Check first review
    review_data = data["reviews"][0]
    assert review_data["id"] == review1.id
    assert review_data["title"] == "Excellent food and service! Best place in the city..."
    assert review_data["thumbnail_url"] == "https://images.yelp.com/thumb1.jpg"
    assert review_data["source"]["url"] == "https://yelp.com/review/123"
    
    # Check second review
    review_data = data["reviews"][1]
    assert review_data["id"] == review2.id
    assert review_data["thumbnail_url"] is None
    assert review_data["source"]["url"] == "https://google.com/review/456"


@pytest.mark.timeout(120)
def test_get_place_first_thumbnail_property(client, test_db):
    """Test that the first_thumbnail property works correctly"""
    PlaceFactory._meta.sqlalchemy_session = test_db
    UserFactory._meta.sqlalchemy_session = test_db
    
    # Create two different users for the reviews
    user1 = UserFactory.create(username="thumbuser1", email="thumbuser1@example.com")
    user2 = UserFactory.create(username="thumbuser2", email="thumbuser2@example.com")
    test_db.commit()
    
    # Create a place
    place = PlaceFactory.create(
        name="Test Restaurant",
        geom=from_shape(Point(-122.419, 37.775), srid=4326)
    )
    test_db.commit()
    
    # Initially no thumbnail
    assert place.first_thumbnail is None
    
    # Add review without thumbnail
    review1 = Review(
        rating=4,
        comment="Good food",
        user_id=user1.id,
        place_id=place.id
    )
    test_db.add(review1)
    test_db.commit()
    
    # Still no thumbnail
    test_db.refresh(place)
    assert place.first_thumbnail is None
    
    # Add review with thumbnail
    review2 = Review(
        rating=5,
        comment="Amazing!",
        thumbnail_url="https://example.com/thumb.jpg",
        user_id=user2.id,  # Different user
        place_id=place.id
    )
    test_db.add(review2)
    test_db.commit()
    
    # Now should have thumbnail
    test_db.refresh(place)
    assert place.first_thumbnail == "https://example.com/thumb.jpg"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
