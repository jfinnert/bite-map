from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from api.router import api_router

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Bite Map API",
    description="API for mapping food videos from social media",
    version="0.0.1",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - will be restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to Bite Map API!"}

# Health check endpoint
@app.get("/healthz")
async def health_check():
    return {"status": "ok"}
