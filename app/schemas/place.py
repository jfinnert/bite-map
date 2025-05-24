from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Union
from datetime import datetime


class PlaceCreate(BaseModel):
    """Schema for creating a new place"""
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    lat: float
    lng: float


class PlaceResponse(BaseModel):
    """Schema for place responses"""
    id: int
    name: str
    slug: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    lat: float = Field(..., description="Latitude of the location")
    lng: float = Field(..., description="Longitude of the location")
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True
    }


class SourceResponse(BaseModel):
    """Schema for source responses"""
    id: int
    url: HttpUrl
    platform: str
    status: str
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class ReviewResponse(BaseModel):
    """Schema for review responses"""
    id: int
    title: Optional[str] = None
    thumbnail_url: Optional[HttpUrl] = None
    source: SourceResponse
    
    model_config = {
        "from_attributes": True
    }


class PlaceDetailResponse(PlaceResponse):
    """Schema for detailed place responses including reviews"""
    reviews: List[ReviewResponse] = []
    
    model_config = {
        "from_attributes": True
    }


class PlaceListMeta(BaseModel):
    """Pagination metadata for place list responses"""
    next: Optional[int] = None


class PlaceListResponse(BaseModel):
    """Wrapper for paginated place list responses"""
    items: List[PlaceResponse]
    meta: PlaceListMeta
