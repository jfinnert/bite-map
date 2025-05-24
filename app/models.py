from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint, func, event, Text as AlchemyText # Use Text as AlchemyText to avoid conflict if user defines TEXT
from sqlalchemy.orm import relationship, declarative_base, declared_attr
from sqlalchemy.dialects.postgresql import TEXT # This is the one the user had
import os

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
    # __table_args__ = {'extend_existing': True} # Temporarily removed

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    address = Column(String)
    latitude = Column(String)
    longitude = Column(String)
    location = Column(String, nullable=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    source = relationship("Source", back_populates="places")
    reviews = relationship("Review", back_populates="place")

class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint('user_id', 'place_id', name='uq_user_place_review'),)
    # Removed extend_existing from here as well

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(TEXT) # Using postgresql.TEXT
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    place_id = Column(Integer, ForeignKey("places.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="reviews")
    place = relationship("Place", back_populates="reviews")
