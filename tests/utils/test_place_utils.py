import pytest
import sys
import os
import logging
from unittest import mock

# Add the app module to path if needed
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'app'))

# Import the functions we want to test - try both path styles
try:
    # Try app-prefixed imports first
    from utils.place_utils import format_place_slug
    try:
        from utils.nlp.place_extractor import extract_place
        has_extractor = True
    except ImportError:
        has_extractor = False
    from utils.geocoder import geocode
    
    print("Using app-prefixed imports")
except ImportError:
    try:
        # Try direct imports
        from utils.place_utils import format_place_slug
        try:
            from utils.nlp.place_extractor import extract_place
            has_extractor = True
        except ImportError:
            has_extractor = False
        from utils.geocoder import geocode
        
        print("Using direct imports")
    except ImportError:
        # If neither works, we'll get import errors during tests
        print("WARNING: Could not import required modules")

def test_format_place_slug():
    """Test the slug formatting function."""
    # Test basic slug creation
    assert format_place_slug("Joe's Pizza") == "joe-s-pizza"
    
    # Test with city
    assert format_place_slug("Joe's Pizza", "New York") == "joe-s-pizza-new-york"
    
    # Test with special characters and spaces
    assert format_place_slug("Café & Restaurant", "Montréal") == "cafe-restaurant-montreal"
    
    # Test length limitation
    long_name = "This is an extremely long restaurant name that should be truncated according to the slug function"
    assert len(format_place_slug(long_name)) <= 60
    

@pytest.mark.skipif(not has_extractor, reason="Place extractor module not available")
def test_extract_place():
    """Test the place extraction from text."""
    # Mock the NLP processor
    with mock.patch('utils.nlp.place_extractor.nlp') as mock_nlp:
        # Configure the mock to return recognized entities
        mock_entities = mock.MagicMock()
        mock_entities.ents = [
            mock.MagicMock(text="Joe's Pizza", label_="ORG"),
            mock.MagicMock(text="New York", label_="GPE")
        ]
        mock_nlp.return_value = mock_entities
        
        # Test extraction from a string
        text = "I visited Joe's Pizza in New York and it was amazing!"
        result = extract_place(text)
        
        # Check that the function extracted the right entities
        assert result["name"] == "Joe's Pizza"
        assert result["hint_loc"] == "New York"
        
        # Test with no recognizable place
        mock_entities.ents = []
        mock_nlp.return_value = mock_entities
        
        result = extract_place("This text has no place mentions")
        assert result is None or result == {}


def test_geocoder():
    """Test the geocoding functionality with mocked API responses."""
    # Set up logging capture
    logger = logging.getLogger('utils.geocoder')
    
    # Mock the httpx client
    with mock.patch('httpx.get') as mock_get:
        # Configure the mock to return a successful response
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
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
            ],
            "status": "OK"
        }
        mock_get.return_value = mock_response
        
        # Mock the API key - the key name might be different in your implementation
        # We'll try GOOGLE_KEY, GOOGLE_MAPS_KEY, and GEOCODING_KEY
        with mock.patch.dict(os.environ, {
            "GOOGLE_KEY": "fake_key", 
            "GOOGLE_MAPS_KEY": "fake_key",
            "GEOCODING_KEY": "fake_key"
        }):
            # Test geocoding a place
            result = geocode("Joe's Pizza", "New York")
            
            # Make sure we got a result
            assert result is not None, "Geocoder returned None instead of results"
            
            # Verify the result structure
            assert result["name"] == "Joe's Pizza"
            assert result["address"] == "Joe's Pizza, Carmine St, New York, NY 10014, USA"
            assert result["lat"] == 40.730610
            assert result["lng"] == -73.935242
            assert result["place_id"] == "ChIJrTLr-DuuEmsRBfy61i59si0"
            assert "restaurant" in result["types"]
            
        # Test with missing API key
        with mock.patch.dict(os.environ, {}, clear=True):
            result = geocode("Joe's Pizza", "New York")
            assert result is None
