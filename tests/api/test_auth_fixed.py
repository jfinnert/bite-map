import os
import sys
import pytest
from unittest import mock
from fastapi import status
from jose import jwt
from datetime import datetime, timedelta

# Add the app directory to the Python path
project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_dir)

# Import our application
from app.main import app
from app.models import User
from app.core.auth import (
    authenticate_user, 
    create_access_token, 
    get_current_user,
    get_password_hash,
    SECRET_KEY,
    ALGORITHM
)

# Test register endpoint
def test_register_endpoint_success(client, test_db):
    """Test successful user registration via the endpoint."""
    # Prepare test data
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
    }
    
    # Make the request
    response = client.post("/api/auth/register", json=user_data)
    
    # Check the response
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data  # Password should not be returned
    
    # Verify user was actually stored in the test database
    user = test_db.query(User).filter(User.username == "testuser").first()
    assert user is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"

def test_register_endpoint_duplicate_username(client, test_db):
    """Test registration with existing username."""
    # Create a user first
    hashed_password = get_password_hash("testpassword")
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password,
    )
    test_db.add(user)
    test_db.commit()
    
    # Try to register with same username
    user_data = {
        "username": "testuser",
        "email": "another@example.com",
        "password": "testpassword",
    }
    
    # Make the request
    response = client.post("/api/auth/register", json=user_data)
    
    # Check the response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    # Check that the error is about duplicate username
    assert "already registered" in response.json()["detail"].lower()

def test_login_endpoint_success(client, test_db):
    """Test successful login via the token endpoint."""
    # Create a test user
    hashed_password = get_password_hash("testpassword")
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password,
    )
    test_db.add(user)
    test_db.commit()
    
    # Login
    response = client.post(
        "/api/auth/token",
        data={"username": "testuser", "password": "testpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Verify token is valid JWT
    token = data["access_token"]
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "testuser"
    assert "exp" in payload

def test_login_endpoint_failed_auth(client, test_db):
    """Test login with invalid credentials."""
    # Create a test user
    hashed_password = get_password_hash("testpassword")
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password,
    )
    test_db.add(user)
    test_db.commit()
    
    # Login with wrong password
    response = client.post(
        "/api/auth/token",
        data={"username": "testuser", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # Check that error mentions incorrect credentials
    assert "incorrect" in response.json()["detail"].lower()

def test_get_current_user_endpoint(client, test_db):
    """Test the /me endpoint to get current user info."""
    # Create a test user
    hashed_password = get_password_hash("testpassword")
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password,
    )
    test_db.add(user)
    test_db.commit()
    
    # Login to get a token
    login_response = client.post(
        "/api/auth/token",
        data={"username": "testuser", "password": "testpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = login_response.json()["access_token"]
    
    # Use token to access /me endpoint
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
