import pytest
import os
import sys
from unittest import mock
import tempfile
import json

# Import worker functions directly
from worker import process_queued_links, mock_extract_video_data, parse_address


def test_mock_extract_video_data():
    """Test the mock video data extraction function."""
    # Test YouTube pizza URL
    pizza_url = "https://www.youtube.com/watch?v=pizza_video"
    result = mock_extract_video_data(pizza_url, "youtube")
    assert "Pizza" in result["title"]
    assert "Joe's Pizza" in result["description"]
    
    # Test YouTube burger URL
    burger_url = "https://www.youtube.com/watch?v=burger_video"
    result = mock_extract_video_data(burger_url, "youtube")
    assert "Burger" in result["title"]
    assert "In-N-Out Burger" in result["description"]
    
    # Test generic URL
    generic_url = "https://www.tiktok.com/@user/video/123456"
    result = mock_extract_video_data(generic_url, "tiktok")
    assert "Food Review" == result["title"]


def test_parse_address():
    """Test the address parser function."""
    # Test with full address
    address = "Joe's Pizza, Carmine St, New York, NY 10014, USA"
    parts = parse_address(address)
    
    assert parts["country"] == "USA"
    assert "NY" in parts["state"]
    assert "New York" in parts["city"]
    
    # Test with shorter address
    address = "Los Angeles, CA, USA"
    parts = parse_address(address)
    
    assert parts["country"] == "USA"
    assert "CA" in parts["state"]


def test_process_queued_links():
    """Test the worker's process_queued_links function with mocked dependencies."""
    with mock.patch("worker.SessionLocal") as mock_session_local:
        # Mock the database session
        mock_db = mock.MagicMock()
        mock_session_local.return_value = mock_db
        
        # Create mock sources
        mock_source = mock.MagicMock()
        mock_source.id = 1
        mock_source.url = "https://www.youtube.com/watch?v=test123"
        mock_source.platform = "youtube"
        mock_source.status = "queued"
        
        # Set up the session query to return our mock source
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_source]
        
        # Mock the extract_place function
        with mock.patch("worker.extract_place") as mock_extract:
            mock_extract.return_value = {
                "name": "Joe's Pizza", 
                "hint_loc": "NYC"
            }
            
            # Mock the geocode function
            with mock.patch("worker.geocode") as mock_geocode:
                mock_geocode.return_value = {
                    "name": "Joe's Pizza",
                    "address": "Joe's Pizza, Carmine St, New York, NY 10014, USA",
                    "lat": 40.730610,
                    "lng": -73.935242,
                    "place_id": "ChIJrTLr-DuuEmsRBfy61i59si0",
                    "types": ["restaurant", "food"]
                }
                
                # Mock the find_nearby_duplicate function
                with mock.patch("worker.find_nearby_duplicate") as mock_find_duplicate:
                    mock_find_duplicate.return_value = None  # No duplicates
                    
                    # Call the function
                    process_queued_links()
                    
                    # Verify the source status was updated
                    assert mock_source.status == "processed"
                    
                    # Verify a place was added to the database
                    mock_db.add.assert_called()
                    mock_db.commit.assert_called()
