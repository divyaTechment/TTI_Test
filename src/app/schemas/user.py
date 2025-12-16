"""
User-related Pydantic schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator

from .base import BaseResponseSchema


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    is_active: bool = Field(True, description="Whether user is active")
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format."""
        if not v.isalnum():
            raise ValueError('Username must contain only alphanumeric characters')
        return v.lower()


class UserCreate(UserBase):
    """Schema for creating a new user."""
    
    password: str = Field(..., min_length=8, description="User password")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    
    email: Optional[EmailStr] = Field(None, description="User email address")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    is_active: Optional[bool] = Field(None, description="Whether user is active")
    
    @validator('username')
    def validate_username(cls, v):
        """Validate username format."""
        if v is not None and not v.isalnum():
            raise ValueError('Username must contain only alphanumeric characters')
        return v.lower() if v else v


class UserLogin(BaseModel):
    """Schema for user login."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    confirm_password: str = Field(..., description="User Confirm password")


class UserResponse(BaseResponseSchema):
    """Schema for user response."""
    
    email: str = Field(..., description="User email address")
    username: str = Field(..., description="Username")
    full_name: Optional[str] = Field(None, description="Full name")
    is_active: bool = Field(..., description="Whether user is active")
    is_verified: bool = Field(..., description="Whether user is verified")
    is_verified: bool = Field(..., description="Whether user is verified")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")


class UserProfile(UserResponse):
    """Schema for user profile (includes sensitive information)."""
    
    pass


class PasswordChange(BaseModel):
    """Schema for password change."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class Token(BaseModel):
    """Schema for authentication token."""
    
    access_token: str = Field(..., description="Access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenData(BaseModel):
    """Schema for token data."""
    
    user_id: Optional[int] = None
    email: Optional[str] = None
