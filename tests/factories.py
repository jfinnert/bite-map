"""
Factory functions for creating test data.
"""
from app.core.auth import get_password_hash

def create_user(db, username="testuser", email="test@example.com", password="testpassword", 
               full_name=None, is_active=True, commit=True):
    """
    Create a test user with sane defaults.
    
    Args:
        db: SQLAlchemy session
        username: User's username
        email: User's email
        password: Plain text password (will be hashed)
        full_name: User's full name (optional)
        is_active: Whether user is active
        commit: Whether to commit the transaction (set False if using in a test with transaction rollback)
        
    Returns:
        User object
    """
    # Import here to avoid circular imports
    from app.models import User
    
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
    
    Args:
        client: TestClient instance
        username: Username to authenticate
        password: Password to authenticate
        
    Returns:
        JWT token string
    """
    response = client.post(
        "/api/auth/token",
        data={"username": username, "password": password}
    )
    assert response.status_code == 200, f"Failed to get token: {response.json()}"
    return response.json()["access_token"]
