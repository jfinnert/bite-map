# filepath: /Users/josh/Python/3.7/Bite Map Project/bite-map/tests/api/test_auth.py
import pytest
from unittest import mock
from fastapi import status
from fastapi.testclient import TestClient
from datetime import datetime

# Import app early to avoid import order issues
from main import app

def get_test_client():
    """Get a fresh test client for each test"""
    return TestClient(app)

@pytest.mark.skip(reason="Database connection required")
def test_register_user():
    """Test user registration endpoint."""
    # Skipped because it requires database access
    pass

def test_login():
    """Test user login and token generation."""
    # Create mock user for authentication
    mock_user = mock.MagicMock()
    mock_user.username = "testuser"
    
    # Apply auth-related patches
    with mock.patch("api.endpoints.auth.authenticate_user", return_value=mock_user), \
         mock.patch("api.endpoints.auth.create_access_token", return_value="test_access_token"):
        
        # Make login request
        client = get_test_client()
        response = client.post(
            "/api/auth/token",
            data={
                "username": "testuser",
                "password": "password"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["access_token"] == "test_access_token"
        assert result["token_type"] == "bearer"

@pytest.mark.skip(reason="Database connection required")
def test_get_current_user():
    """Test retrieving the current authenticated user."""
    # Skipped because it requires database access
    pass
