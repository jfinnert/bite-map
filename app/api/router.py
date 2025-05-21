from fastapi import APIRouter

from .endpoints import health, ingest, places, auth

api_router = APIRouter()

# Include sub-routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
api_router.include_router(places.router, prefix="/places", tags=["places"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
