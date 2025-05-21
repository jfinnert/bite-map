from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from geoalchemy2.functions import ST_AsGeoJSON, ST_MakeEnvelope

from ...database import get_db
from ...models import Place, Review
from ...schemas.place import PlaceResponse, PlaceDetailResponse

router = APIRouter()

@router.get("", response_model=Dict[str, Any])
async def get_places(
    bbox: Optional[str] = Query(None, description="Bounding box in format: minLng,minLat,maxLng,maxLat"),
    q: Optional[str] = Query(None, description="Text search query"),
    limit: int = Query(50, description="Maximum number of places to return"),
    offset: int = Query(0, description="Number of places to skip"),
    db: Session = Depends(get_db)
):
    """
    Get a list of places, optionally filtered by bounding box or text search.
    
    Returns paginated results with places in GeoJSON format for easy mapping.
    """
    query = db.query(Place)
    
    # Apply bounding box filter if provided
    if bbox:
        try:
            # Parse the bbox parameter
            min_lng, min_lat, max_lng, max_lat = map(float, bbox.split(","))
            
            # Create a PostGIS envelope and filter places within it
            envelope = ST_MakeEnvelope(min_lng, min_lat, max_lng, max_lat, 4326)
            query = query.filter(func.ST_Within(Place.location, envelope))
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Invalid bbox format. Use 'minLng,minLat,maxLng,maxLat'"
            )
    
    # Apply text search filter if provided
    if q:
        search_term = f"%{q}%"
        query = query.filter(
            (Place.name.ilike(search_term)) |
            (Place.address.ilike(search_term)) |
            (Place.city.ilike(search_term))
        )
    
    # Count total matching places (without pagination)
    total_count = query.count()
    
    # Apply pagination
    query = query.order_by(Place.id.desc()).offset(offset).limit(limit)
    
    # Execute query
    places = query.all()
    
    # Convert places to GeoJSON features
    features = []
    for place in places:
        # Get GeoJSON representation of the point geometry
        geojson = db.scalar(ST_AsGeoJSON(place.location))
        geometry = json.loads(geojson)
        
        # Get the number of reviews for this place
        review_count = db.query(func.count(Review.id)).filter(Review.place_id == place.id).scalar()
        
        # Create GeoJSON feature
        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": place.id,
                "name": place.name,
                "address": place.address,
                "slug": place.slug,
                "city": place.city,
                "state": place.state,
                "country": place.country,
                "review_count": review_count
            }
        }
        features.append(feature)
    
    # Return GeoJSON FeatureCollection with pagination metadata
    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "page": offset // limit + 1,
            "pages": (total_count + limit - 1) // limit
        }
    }


@router.get("/{place_id}", response_model=PlaceDetailResponse)
async def get_place(place_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific place, including associated reviews.
    """
    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    
    return place
