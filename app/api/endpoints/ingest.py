from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Optional, List
from pydantic import BaseModel, HttpUrl

# Use absolute imports instead of relative imports
from database import get_db
from models import Source, Review, Place
from schemas.place import PlaceResponse, PlaceDetailResponse
import uuid
import subprocess
import sys
import os

router = APIRouter()

class LinkIngest(BaseModel):
    url: HttpUrl

@router.post("/link")
async def ingest_link(
    link: LinkIngest, 
    background_tasks: BackgroundTasks,
    run_worker: bool = True,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Ingest a URL to be processed and added to the map.
    
    This endpoint accepts a URL, stores it in the database with 'queued' status,
    and returns a confirmation that it was received.
    
    Args:
        link: The URL to ingest
        background_tasks: FastAPI BackgroundTasks for running the worker
        run_worker: Whether to run the worker immediately (True) or let it run on schedule
    """
    try:
        # Determine platform from URL
        platform = "unknown"
        if "youtube.com" in str(link.url) or "youtu.be" in str(link.url):
            platform = "youtube"
        elif "tiktok.com" in str(link.url):
            platform = "tiktok"
        
        # Create a new source record
        source = Source(
            url=str(link.url),
            platform=platform,
            status="queued"
        )
        
        db.add(source)
        db.commit()
        db.refresh(source)
        
        # Run the worker in the background if requested
        if run_worker:
            background_tasks.add_task(run_worker_process)
        
        return {
            "status": "success",
            "message": "Link received and queued for processing",
            "id": source.id,
            "url": source.url,
            "platform": source.platform
        }
    
    except Exception as e:
        # Roll back in case of error
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing link: {str(e)}")


def run_worker_process():
    """Run the worker script as a subprocess."""
    try:
        # Get the path to the worker script
        worker_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "worker.py")
        
        # Run the worker script with the --once flag
        subprocess.run([sys.executable, worker_path, "--once"], check=True)
    except Exception as e:
        print(f"Error running worker: {str(e)}")


@router.get("/link/{source_id}/place", response_model=Optional[PlaceDetailResponse])
async def get_link_place(source_id: int, db: Session = Depends(get_db)):
    """
    Get the place associated with an ingested link.
    
    This endpoint returns the place information for a previously ingested link,
    including all linked reviews.
    """
    # Check if the source exists
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
        
    # Get the review associated with this source
    review = db.query(Review).filter(Review.source_id == source_id).first()
    if not review:
        return None  # No place associated yet
        
    # Get the place
    place = db.query(Place).filter(Place.id == review.place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Associated place not found")
        
    # Return the place with reviews
    return place
