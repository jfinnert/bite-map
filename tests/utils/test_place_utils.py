import pytest
from unittest import mock
import json

from app.utils.nlp.place_extractor import extract_place
from app.utils.geocoder import geocode


def test_extract_place():
    """Test the place extraction from text."""
    # Test with restaurant and location
    text = "I visited Joe's Pizza in NYC and it was amazing!"
    result = extract_place(text)
    
    assert result["name"] == "Joe's Pizza"
    assert result["hint_loc"] == "NYC"
    
    # Test with empty text
    assert extract_place("") == {"name": "", "hint_loc": ""}
    
    # Test with just a restaurant name
    text = "Lombardi's Pizza has the best pizza in the city."
    result = extract_place(text)
    
    assert "Lombardi's Pizza" in result["name"]


def test_geocoder():
    """Test the geocoding functionality with mocked API responses."""
    # Mock the httpx.Client to avoid actual API calls
    with mock.patch("app.utils.geocoder.httpx.Client") as mock_client:
        # Configure the mock response
        mock_response = mock.MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "status": "OK",
            "results": [
                {
                    "formatted_address": "Joe's Pizza, Carmine St, New York, NY 10014, USA",
                    "geometry": {
                        "location": {
                            "lat": 40.730610,
                            "lng": -73.935242
                        }
                    },
                    "place_id": "ChIJrTLr-DuuEmsRBfy61i59si0",
                    "types": ["restaurant", "food", "point_of_interest", "establishment"]
                }
            ]
        }
        
        # Set up the mock client to return our response
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        
        # Test with valid input
        result = geocode("Joe's Pizza", "NYC")
        
        assert result["name"] == "Joe's Pizza"
        assert result["address"] == "Joe's Pizza, Carmine St, New York, NY 10014, USA"
        assert result["lat"] == 40.730610
        assert result["lng"] == -73.935242
        assert result["place_id"] == "ChIJrTLr-DuuEmsRBfy61i59si0"
        
        # Test with empty string
        with mock.patch("app.utils.geocoder.logger") as mock_logger:
            result = geocode("")
            assert result is None
            mock_logger.warning.assert_called_once()
