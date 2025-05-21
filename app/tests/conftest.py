import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.append('/app')
from main import app

# Create a test client
client = TestClient(app)
