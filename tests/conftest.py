import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.main import app

# Create a test client
client = TestClient(app)
