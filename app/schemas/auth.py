from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for data stored in JWT token."""
    username: Optional[str] = None

class UserBase(BaseModel):
    """Base schema for user data."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str

class UserResponse(UserBase):
    """Schema for user responses."""
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }
