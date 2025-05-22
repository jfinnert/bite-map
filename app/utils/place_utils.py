from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from sqlalchemy import func
from geoalchemy2.functions import ST_DWithin, ST_Distance, ST_MakePoint
from typing import Optional, List, Dict, Any

from models import Place


def find_nearby_duplicate(db: Session, lat: float, lng: float, name: str = None, distance_meters: int = 100) -> Optional[Place]:
    """
    Find a place that might be a duplicate based on geographic proximity
    and optionally similar name.
    
    Args:
        db: Database session
        lat: Latitude of the new place
        lng: Longitude of the new place
        name: Optional name of the new place for name similarity check
        distance_meters: Maximum distance in meters to consider as duplicate
        
    Returns:
        A Place instance if a potential duplicate is found, None otherwise.
    """
    # Create a PostGIS point from lat/lng
    point = func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)
    
    # Query for nearby places
    query = db.query(Place).filter(
        ST_DWithin(
            Place.location,
            point,
            distance_meters  # Distance in meters
        )
    )
    
    # If name is provided, prioritize places with similar names
    if name:
        # First check exact name match
        exact_match = query.filter(func.lower(Place.name) == name.lower()).first()
        if exact_match:
            return exact_match
            
        # Then check for similarity in the name
        # Use SQL function similarity which returns values between 0 and 1
        similar_places = query.filter(
            func.similarity(func.lower(Place.name), name.lower()) > 0.4
        ).order_by(
            func.similarity(func.lower(Place.name), name.lower()).desc()
        ).all()
        
        if similar_places:
            return similar_places[0]
    
    # If no name matches or no name provided, return the closest place
    closest_place = query.order_by(
        ST_Distance(Place.location, point)
    ).first()
    
    return closest_place
    

def format_place_slug(name: str, city: str = None) -> str:
    """
    Generate a URL-friendly slug for a place based on its name and city.
    
    Args:
        name: The place name
        city: Optional city name
        
    Returns:
        A URL-friendly slug
    """
    import re
    from slugify import slugify
    
    # Basic slug from name
    slug = slugify(name)
    
    # Add city suffix if provided
    if city:
        city_slug = slugify(city)
        slug = f"{slug}-{city_slug}"
        
    # Ensure it's not too long
    if len(slug) > 60:
        slug = slug[:60]
        
    return slug
