import pytest
import os
from fastapi.testclient import TestClient
from unittest import mock
from fastapi import status
import json

# Import the test client from conftest
from conftest import client


def test_register_user():
    """Test user registration."""
    with mock.patch("api.endpoints.auth.get_db") as mock_get_db:
        # Mock the database session
        mock_session = mock.MagicMock()
        mock_get_db.return_value = mock_session
        
        # Configure mock to simulate user not existing
        mock_query = mock_session.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # User doesn't exist
        
        # User data for registration
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "securepassword"
        }
        
        # Mock password hashing
        with mock.patch("api.endpoints.auth.get_password_hash") as mock_hash:
            mock_hash.return_value = "hashed_password"
            
            # Register user
            response = client.post(
                "/api/auth/register",
                json=user_data
            )
            
            # Check response
            assert response.status_code == status.HTTP_201_CREATED
            result = response.json()
            assert result["username"] == user_data["username"]
            assert result["email"] == user_data["email"]
            assert "password" not in result
            
            # Verify user was added to the database
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()


def test_login():
    """Test user login and token generation."""
    with mock.patch("api.endpoints.auth.authenticate_user") as mock_auth:
        # Create mock user
        mock_user = mock.MagicMock()
        mock_user.username = "testuser"
        
        # Configure auth to return our mock user
        mock_auth.return_value = mock_user
        
        # Mock token creation
        with mock.patch("api.endpoints.auth.create_access_token") as mock_create_token:
            mock_create_token.return_value = "test_access_token"
            
            # Attempt login
            response = client.post(
                "/api/auth/token",
                data={
                    "username": "testuser",
                    "password": "password"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            # Check response
            assert response.status_code == status.HTTP_200_OK
            result = response.json()
            assert result["access_token"] == "test_access_token"
            assert result["token_type"] == "bearer"


def test_get_current_user():
    """Test retrieving the current authenticated user."""
    with mock.patch("api.endpoints.auth.get_current_user") as mock_get_user:
        # Create mock user
        mock_user = mock.MagicMock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.full_name = "Test User"
        mock_user.is_active = True
        
        # Configure to return our mock user
        mock_get_user.return_value = mock_user
        
        # Get current user
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer test_token"}
        )
        
        # Check response
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
