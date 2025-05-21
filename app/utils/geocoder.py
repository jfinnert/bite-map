import os
import logging
import time
import httpx
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

def geocode(query: str, hint_location: str = None) -> Optional[Dict[str, Any]]:
    """
    Convert a place name and optional location hint to geographic coordinates
    using Google Maps Geocoding API.
    
    Args:
        query: The place name or address to geocode
        hint_location: Optional location hint to narrow down results (e.g., city or area)
        
    Returns:
        A dictionary containing geocoding results with:
        {
            "name": "Formatted place name",
            "address": "Full address",
            "lat": latitude,
            "lng": longitude,
            "place_id": "Google Maps place_id",
            "types": ["list", "of", "place", "types"]
        }
        Or None if geocoding failed.
    """
    if not query:
        logger.warning("Empty query passed to geocode function")
        return None
        
    api_key = os.getenv("GOOGLE_KEY")
    if not api_key:
        logger.error("GOOGLE_KEY environment variable not set")
        return None
        
    # Combine query and hint location if provided
    search_query = query
    if hint_location:
        search_query = f"{query}, {hint_location}"
        
    # Prepare the geocoding request
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": search_query,
        "key": api_key,
    }
    
    # Add parameters for food-related results
    if "restaurant" not in search_query.lower() and "food" not in search_query.lower():
        params["types"] = "restaurant|food|cafe|meal_takeaway|bakery"
        
    url = f"{base_url}?{urlencode(params)}"
    
    max_retries = 3
    retry_delay = 0.1  # Start with 100ms
    
    # Try the request with exponential backoff
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                
                if data["status"] == "OK" and len(data["results"]) > 0:
                    result = data["results"][0]
                    
                    # Extract the useful fields
                    return {
                        "name": query,  # Keep original name
                        "address": result["formatted_address"],
                        "lat": result["geometry"]["location"]["lat"],
                        "lng": result["geometry"]["location"]["lng"],
                        "place_id": result["place_id"],
                        "types": result["types"],
                    }
                elif data["status"] == "ZERO_RESULTS":
                    logger.warning(f"No geocoding results found for: {search_query}")
                    return None
                else:
                    logger.error(f"Geocoding error: {data['status']}")
                    
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        return None
                        
        except Exception as e:
            logger.error(f"Error during geocoding: {str(e)}")
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                return None
                
    return None
