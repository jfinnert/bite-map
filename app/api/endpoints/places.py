from fastapi import APIRouter, Depends, HTTPException, Query, Path, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, text, desc, Float
from typing import List, Optional, Dict, Any, Annotated, Union
from geoalchemy2.functions import ST_AsGeoJSON, ST_MakeEnvelope, ST_Within, ST_GeomFromText
import json
import logging
import asyncio
import functools

# Use absolute imports instead of relative imports
from app.core.auth import get_current_user, get_current_user_optional
from app.database import get_db
from app.models import Place, Review, User
from app.schemas.place import PlaceResponse, PlaceDetailResponse, PlaceListResponse, PlaceListMeta

# Configure logging
logger = logging.getLogger(__name__)

def timeout_after(seconds: float):
    """Decorator to add timeout to async functions for performance safety."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                logger.warning(f"Function {func.__name__} timed out after {seconds} seconds")
                raise HTTPException(status_code=408, detail="Request timeout")
        return wrapper
    return decorator

router = APIRouter()

def get_places(db: Session):
    """Get a list of all places."""
    return db.query(Place).all()
    
def get_place_by_slug(db: Session, slug: str):
    """Get a place by its slug."""
    return db.query(Place).filter(Place.slug == slug).first()

@router.get("/me/favorites", response_model=Dict[str, Any])
async def get_my_favorites(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """
    Get the current user's favorite places.
    This endpoint is protected and requires authentication.
    """
    # In a real implementation, this would use a user_favorites table
    # For now, we'll just return a sample of places
    
    places = db.query(Place).order_by(func.random()).limit(5).all()
    
    # Convert places to GeoJSON features
    features = []
    for place in places:
        # Get GeoJSON representation of the point geometry
        geojson = db.scalar(ST_AsGeoJSON(place.geom))
        geometry = json.loads(geojson) if geojson else None
        
        # Create GeoJSON feature
        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": place.id,
                "name": place.name,
                "address": place.address,
                "slug": place.slug,
                "city": getattr(place, "city", None),
                "state": getattr(place, "state", None),
                "country": getattr(place, "country", None),
                "favorited": True  # Since these are favorites
            }
        }
        features.append(feature)
    
    # Return GeoJSON FeatureCollection
    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "total": len(features),
            "user_id": current_user.id
        }
    }

@router.get("", response_model=PlaceListResponse)
@timeout_after(30.0)  # 30 second timeout for database queries
async def get_places(
    response: Response,
    bbox: Optional[str] = Query(None, description="Bounding box in format: minLng,minLat,maxLng,maxLat"),
    q: Optional[str] = Query(None, description="Text search query"),
    after_id: Optional[int] = Query(None, description="Keyset pagination: return results with id < after_id"),
    per_page: int = Query(20, ge=1, le=50, description="Results per page (max 50)"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    List places with optional bounding box, text search, and keyset pagination.
    
    - **bbox**: minLng,minLat,maxLng,maxLat (WGS84, SRID 4326)
    - **q**: text search on name (trigram, case-insensitive)
    - **after_id**: keyset pagination (return places with id < after_id)
    - **per_page**: results per page (max 50, default 20)
    
    Response:
    ```json
    {
      "items": [PlaceOut, ...],
      "meta": {"next": int|null}
    }
    ```
    """
    # Set cache header for 30 seconds
    response.headers["Cache-Control"] = "public, max-age=30"
    
    # Start with base query, order by newest first
    query = db.query(Place).order_by(desc(Place.id))
    
    # Apply keyset pagination if after_id is provided
    if after_id:
        query = query.filter(Place.id < after_id)
    
    # Apply bounding box filter if provided
    if bbox:
        try:
            # Parse the bbox parameter
            min_lng, min_lat, max_lng, max_lat = map(float, bbox.split(","))
            
            # Create a PostGIS envelope and filter places within it
            envelope = ST_MakeEnvelope(min_lng, min_lat, max_lng, max_lat, 4326)
            query = query.filter(ST_Within(Place.geom, envelope))
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Invalid bbox format. Use 'minLng,minLat,maxLng,maxLat'"
            )
    
    # Apply text search filter if provided using ILIKE for case-insensitive partial matching
    if q:
        # Use ILIKE for simple case-insensitive partial matching (fallback from trigram)
        # This works universally without requiring pg_trgm extension
        query = query.filter(Place.name.ilike(f'%{q}%'))
    
    # Get one more than per_page to determine if there are more results
    places = query.limit(per_page + 1).all()
    
    # Check if there are more results
    has_more = len(places) > per_page
    
    # Trim to per_page
    if has_more:
        next_id = places[per_page - 1].id  # The id to use for the next page
        places = places[:per_page]
    else:
        next_id = None
    
    # Convert to response model using the new lat/lng properties
    items = []
    for place in places:
        items.append({
            "id": place.id,
            "name": place.name,
            "slug": getattr(place, "slug", f"place-{place.id}"),
            "address": place.address,
            "city": getattr(place, "city", None),
            "state": getattr(place, "state", None),
            "country": getattr(place, "country", None),
            "postal_code": getattr(place, "postal_code", None),
            "lat": place.lat,  # Use the property that extracts from geom
            "lng": place.lng,  # Use the property that extracts from geom
            "created_at": place.created_at,
            "updated_at": place.updated_at
        })
    
    # Return paginated response
    return {
        "items": items,
        "meta": {
            "next": next_id
        }
    }


@router.get("/{place_id}", response_model=PlaceDetailResponse)
@timeout_after(30.0)  # 30 second timeout for database queries
async def get_place(
    place_id: int, 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get detailed information about a specific place by ID.
    
    This endpoint returns comprehensive place details including:
    - Basic place information (name, address, coordinates)
    - List of associated reviews with titles and source URLs
    - Review thumbnails when available
    - First thumbnail URL from any review (via place.first_thumbnail property)
    
    Parameters:
    - **place_id**: The unique identifier for the place
    
    Returns:
    - **PlaceDetailResponse**: Complete place details with nested review data
    
    Raises:
    - **404**: Place not found
    """
    # Query the place with reviews
    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    
    # Get all reviews for this place with their source URLs
    reviews = db.query(Review).filter(Review.place_id == place_id).all()
    
    # Build review response data
    review_responses = []
    for review in reviews:
        review_responses.append({
            "id": review.id,
            "title": review.comment[:50] + "..." if review.comment and len(review.comment) > 50 else review.comment,
            "thumbnail_url": review.thumbnail_url,
            "source": {
                "id": review.id,  # Using review ID as source ID for now
                "url": review.source_url or "https://example.com/review",  # Fallback URL
                "platform": "unknown",  # Could be extracted from source_url domain
                "status": "active",
                "created_at": review.created_at
            }
        })
    
    # Prepare the detailed response
    place_detail = {
        "id": place.id,
        "name": place.name,
        "slug": getattr(place, "slug", f"place-{place.id}"),
        "address": place.address,
        "city": getattr(place, "city", None),
        "state": getattr(place, "state", None),
        "country": getattr(place, "country", None),
        "postal_code": getattr(place, "postal_code", None),
        "lat": place.lat,
        "lng": place.lng,
        "created_at": place.created_at,
        "updated_at": place.updated_at,
        "reviews": review_responses
    }
    
    return place_detail
