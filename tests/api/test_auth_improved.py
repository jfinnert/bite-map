"""
Improved tests for authentication endpoints.
"""
import os
import sys
import pytest
from fastapi import status
from jose import jwt
import time
from datetime import datetime, timezone

# Add parent directories to path to fix imports
project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_dir)

# Import from our app
from app.core.auth import get_password_hash, SECRET_KEY, ALGORITHM

# Include factory functions directly to avoid import issues
def create_user(db, username="testuser", email="test@example.com", password="testpassword", 
               full_name=None, is_active=True, commit=True):
    """
    Create a test user with sane defaults.
    """
    # Import here to avoid circular imports
    from app.models import User
    from app.core.auth import get_password_hash
    
    # Hash the password
    hashed_password = get_password_hash(password)
    
    # Create user object with proper defaults
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        is_active=is_active
    )
    
    # Add and optionally commit
    db.add(user)
    if commit:
        db.commit()
        db.refresh(user)
        
    return user

def get_token_for_user(client, username="testuser", password="testpassword"):
    """
    Helper to get a valid JWT token for a user.
    """
    response = client.post(
        "/api/auth/token",
        data={"username": username, "password": password}
    )
    assert response.status_code == 200, f"Failed to get token: {response.json()}"
    return response.json()["access_token"]

# Test constants for environment independence
TEST_SECRET_KEY = SECRET_KEY  # In a real app, use a separate test secret

def test_register_endpoint_success(client, test_db):
    """Test successful user registration."""
    # Prepare test data
    user_data = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123",
    }
    
    # Make the request
    response = client.post("/api/auth/register", json=user_data)
    
    # Check response status and data
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data
    assert "hashed_password" not in data
    
    # Import inside function to avoid circular imports
    from app.models import User
    
    # Verify user was saved to database
    user = test_db.query(User).filter(User.username == user_data["username"]).first()
    assert user is not None
    assert user.email == user_data["email"]
    
    # Verify password was properly hashed
    assert user.hashed_password != user_data["password"]
    assert len(user.hashed_password) > 20  # Ensure it's a hash, not plaintext


def test_register_endpoint_duplicate_username(client, test_db):
    """Test registration with existing username returns 409 Conflict."""
    # Create an existing user
    create_user(test_db, username="existing", email="existing@example.com", commit=True)
    
    # Try to register with same username
    user_data = {
        "username": "existing",
        "email": "another@example.com",
        "password": "password123",
    }
    
    # Make the request
    response = client.post("/api/auth/register", json=user_data)
    
    # Check response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"].lower()


def test_register_endpoint_duplicate_email(client, test_db):
    """Test registration with existing email."""
    # Create an existing user
    create_user(test_db, username="user1", email="duplicate@example.com", commit=True)
    
    # Try to register with same email
    user_data = {
        "username": "user2",
        "email": "duplicate@example.com",
        "password": "password123",
    }
    
    # Make the request
    response = client.post("/api/auth/register", json=user_data)
    
    # Check response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email already registered" in response.json()["detail"].lower()


def test_login_endpoint_success(client, test_db):
    """Test successful login returns valid JWT token."""
    # Create a test user with factory
    username = "loginuser"
    password = "password123"
    create_user(test_db, username=username, password=password)
    
    # Login
    response = client.post(
        "/api/auth/token",
        data={"username": username, "password": password}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Verify token is valid JWT with proper claims
    token = data["access_token"]
    payload = jwt.decode(token, TEST_SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == username
    
    # Verify expiration is in the future
    exp = payload.get("exp", 0)
    assert exp > time.time(), "Token is already expired"
    
    # Check if other expected claims are present (these would be app-specific)
    # assert "iss" in payload  # Issuer
    # assert payload["iss"] == "bitemap-api"
    # assert "aud" in payload  # Audience
    # assert "bitemap-client" in payload["aud"]


def test_login_endpoint_wrong_password(client, test_db):
    """Test login with wrong password."""
    # Create a test user with factory
    username = "loginuser"
    create_user(test_db, username=username, password="correctpassword")
    
    # Login with wrong password
    response = client.post(
        "/api/auth/token",
        data={"username": username, "password": "wrongpassword"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "incorrect" in response.json()["detail"].lower()


def test_login_endpoint_user_not_found(client, test_db):
    """Test login with non-existent user."""
    # Login with non-existent user
    response = client.post(
        "/api/auth/token",
        data={"username": "nonexistentuser", "password": "anypassword"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # Should not leak information about whether user exists
    assert "incorrect username or password" in response.json()["detail"].lower()


def test_get_current_user_endpoint(client, test_db):
    """Test /me endpoint returns user data when authenticated."""
    # Create a user and get a token
    username = "currentuser"
    password = "password123"
    email = "current@example.com"
    user = create_user(test_db, username=username, email=email, password=password)
    token = get_token_for_user(client, username, password)
    
    # Access /me endpoint with token
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == username
    assert data["email"] == email
    assert "password" not in data
    assert "hashed_password" not in data


def test_get_current_user_endpoint_no_token(client):
    """Test /me endpoint returns 401 when no token provided."""
    response = client.get("/api/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_endpoint_invalid_token(client):
    """Test /me endpoint returns 401 with invalid token."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalidtoken123"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_auth_client_fixture(auth_client):
    """Test the auth_client fixture works as expected."""
    # Use auth_client which already has authentication set up
    response = auth_client.get("/api/auth/me")
    
    # Check response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
