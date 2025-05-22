#!/usr/bin/env python
"""
Worker script that processes queued links in the database.
"""
import os
import sys
import time
import json
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from typing import Optional, Dict, Any
from geoalchemy2.elements import WKTElement

# Use direct imports when working inside the app directory
from database import SessionLocal
from models import Source, Place, Review
from utils.nlp.place_extractor import extract_place
from utils.geocoder import geocode
from utils.place_utils import find_nearby_duplicate, format_place_slug

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def process_queued_links():
    """
    Fetches links with 'queued' status, extracts place information,
    and creates place entries in the database.
    """
    db = SessionLocal()
    try:
        # Find queued links
        queued_links = db.query(Source).filter(Source.status == "queued").all()
        
        if not queued_links:
            logger.info("No queued links found")
            return
        
        logger.info(f"Found {len(queued_links)} queued links to process")
        
        for link in queued_links:
            logger.info(f"Processing link {link.id}: {link.url}")
            
            try:
                # Mark as processing to avoid duplicate processing
                link.status = "processing"
                db.commit()
                
                # For now we'll use a simple mock implementation
                # In a real implementation, we would use the extractors
                # to get real data from the platform
                
                # Mock video data extraction
                video_data = mock_extract_video_data(link.url, link.platform)
                link.raw_data = json.dumps(video_data)
                
                # Extract place from video data
                text_to_analyze = f"{video_data.get('title', '')} {video_data.get('description', '')}"
                place_info = extract_place(text_to_analyze)
                
                logger.info(f"Extracted place info: {place_info}")
                
                if place_info and place_info["name"]:
                    # Try to geocode the place
                    geo_result = geocode(place_info["name"], place_info["hint_loc"])
                    
                    if geo_result:
                        logger.info(f"Geocoded result: {geo_result['name']} at {geo_result['lat']}, {geo_result['lng']}")
                        
                        # Check for nearby duplicates
                        existing_place = find_nearby_duplicate(
                            db, 
                            geo_result["lat"], 
                            geo_result["lng"], 
                            geo_result["name"]
                        )
                        
                        # Use existing place or create new one
                        place_id = None
                        if existing_place:
                            logger.info(f"Found existing place: {existing_place.name} (id: {existing_place.id})")
                            place_id = existing_place.id
                        else:
                            # Create new place
                            slug = format_place_slug(geo_result["name"], geo_result.get("city"))
                            
                            # Create WKT point from lat/lng
                            point_wkt = f"POINT({geo_result['lng']} {geo_result['lat']})"
                            location = WKTElement(point_wkt, srid=4326)
                            
                            # Parse address components
                            address_parts = parse_address(geo_result["address"])
                            
                            new_place = Place(
                                name=geo_result["name"],
                                slug=slug,
                                address=geo_result["address"],
                                city=address_parts.get("city"),
                                state=address_parts.get("state"),
                                country=address_parts.get("country"),
                                postal_code=address_parts.get("postal_code"),
                                location=location
                            )
                            
                            db.add(new_place)
                            db.flush()  # Get the ID without committing
                            place_id = new_place.id
                            logger.info(f"Created new place: {new_place.name} (id: {new_place.id})")
                        
                        # Create a review linking the source to the place
                        review = Review(
                            source_id=link.id,
                            place_id=place_id,
                            title=video_data.get("title"),
                            thumbnail_url=video_data.get("thumbnail_url")
                        )
                        
                        db.add(review)
                        link.status = "processed"
                    else:
                        logger.warning(f"Could not geocode place: {place_info['name']}")
                        link.status = "geocode_failed"
                else:
                    logger.warning("Could not extract place info from video")
                    link.status = "extraction_failed"
            
            except Exception as e:
                logger.error(f"Error processing link {link.id}: {str(e)}")
                link.status = "error"
                continue
            
            # Update timestamp
            link.updated_at = datetime.now()
            db.add(link)
        
        # Commit all changes
        db.commit()
        logger.info("All queued links processed")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in process_queued_links: {str(e)}")
    finally:
        db.close()

def mock_extract_video_data(url: str, platform: str) -> Dict[str, Any]:
    """
    Mock function to generate fake video data for development.
    This would be replaced by actual extractor calls in production.
    """
    if "youtube" in platform:
        # Generate mock YouTube data
        if "pizza" in url.lower():
            return {
                "title": "BEST Pizza in New York City",
                "description": "We visited Joe's Pizza in NYC and it was amazing! The classic slice is perfect.",
                "thumbnail_url": "https://example.com/pizza.jpg"
            }
        elif "burger" in url.lower():
            return {
                "title": "Ultimate Burger Guide: Los Angeles",
                "description": "In-N-Out Burger is a California institution. Double-double animal style!",
                "thumbnail_url": "https://example.com/burger.jpg"
            }
        else:
            return {
                "title": "Amazing Street Food Tour",
                "description": "Exploring the best food trucks in Austin, Texas. BBQ heaven!",
                "thumbnail_url": "https://example.com/food.jpg"
            }
    else:
        # Generic mock data
        return {
            "title": "Food Review",
            "description": "Trying out this restaurant downtown",
            "thumbnail_url": "https://example.com/generic.jpg"
        }

def parse_address(address: str) -> Dict[str, str]:
    """
    Simple address parser to extract components from a formatted address.
    In a real application, this would be more sophisticated.
    """
    parts = {}
    
    # Very simple parsing - would need improvement in production
    address_parts = address.split(", ")
    
    if len(address_parts) >= 1:
        # Last part usually contains country
        parts["country"] = address_parts[-1]
        
        # Handle addresses with at least state and country
        if len(address_parts) >= 2:
            # Second to last usually has state/province and possibly postal code
            state_part = address_parts[-2]
            state_zip = state_part.split(" ")
            
            # Set the state regardless of whether there's a postal code
            parts["state"] = state_zip[0]
            
            # If there's more than just the state abbreviation, it may include a postal code
            if len(state_zip) >= 2:
                parts["postal_code"] = " ".join(state_zip[1:])
            
            # If we have city info (3+ parts in address)
            if len(address_parts) >= 3:
                parts["city"] = address_parts[-3]
    
    return parts

def run_worker(once=False):
    """Run the worker process."""
    logger.info("Starting worker process")
    
    if once:
        process_queued_links()
    else:
        # Run in a loop, checking for new links periodically
        while True:
            process_queued_links()
            logger.info("Sleeping for 30 seconds")
            time.sleep(30)

if __name__ == "__main__":
    # Check if we should run once or continuously
    run_once = "--once" in sys.argv
    run_worker(once=run_once)
