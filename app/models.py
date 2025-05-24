from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint, func, event, Text as AlchemyText # Use Text as AlchemyText to avoid conflict if user defines TEXT
from sqlalchemy.orm import relationship, declarative_base, declared_attr, object_session
from sqlalchemy.dialects.postgresql import TEXT # This is the one the user had
import os
import json
from geoalchemy2 import Geometry

# Use a single Base for all models
from app.database import Base

class User(Base):
    __tablename__ = "users"
    # __table_args__ = {'extend_existing': True} # Temporarily removed

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    reviews = relationship("Review", back_populates="user")
    sources = relationship("Source", back_populates="user")

class Source(Base):
    __tablename__ = "sources"
    # __table_args__ = {'extend_existing': True} # Temporarily removed

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    url = Column(String, unique=True, index=True)
    description = Column(TEXT) # Using postgresql.TEXT
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="sources")
    places = relationship("Place", back_populates="source")

class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    address = Column(String)
    
    # Use Geometry for all spatial operations (PostgreSQL with PostGIS)
    geom = Column(Geometry(geometry_type='POINT', srid=4326, spatial_index=False), nullable=True)
    
    slug = Column(String, unique=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    source = relationship("Source", back_populates="places")
    reviews = relationship("Review", back_populates="place")
    
    @property
    def lat(self) -> float:
        """Extract latitude from geometry for API responses."""
        if self.geom is not None:
            session = object_session(self)
            if session:
                from geoalchemy2.functions import ST_Y
                return session.scalar(ST_Y(self.geom))
        return None
    
    @property 
    def lng(self) -> float:
        """Extract longitude from geometry for API responses."""
        if self.geom is not None:
            session = object_session(self)
            if session:
                from geoalchemy2.functions import ST_X
                return session.scalar(ST_X(self.geom))
        return None
    
    @property
    def first_thumbnail(self) -> str:
        """Get the first available thumbnail URL from associated reviews."""
        session = object_session(self)
        if session:
            # Query for the first review with a thumbnail_url for this place
            review = session.query(Review).filter(
                Review.place_id == self.id,
                Review.thumbnail_url.isnot(None)
            ).first()
            if review:
                return review.thumbnail_url
        return None

# Add event listeners for Place to generate slug
@event.listens_for(Place, 'before_insert')
@event.listens_for(Place, 'before_update')
def generate_slug_before_save(mapper, connection, place):
    """Generate slug if needed"""
    if not place.slug and place.name:
        from slugify import slugify
        place.slug = slugify(place.name)
        
        # If an integer ID exists, append it to ensure uniqueness
        if place.id:
            place.slug = f"{place.slug}-{place.id}"

class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint('user_id', 'place_id', name='uq_user_place_review'),)

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(TEXT) # Using postgresql.TEXT
    source_url = Column(String, nullable=True)  # URL to the original review
    thumbnail_url = Column(String, nullable=True)  # URL to review thumbnail/image
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    place_id = Column(Integer, ForeignKey("places.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="reviews")
    place = relationship("Place", back_populates="reviews")
