"""
Pydantic schemas for API request/response validation.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""
    name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")


class UserCreate(UserBase):
    """Schema for creating a user."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for user list response."""
    users: List[UserResponse]
    total: int
    skip: int
    limit: int


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    message: str
    details: Optional[dict] = None


class SuccessResponse(BaseModel):
    """Schema for success responses."""
    message: str
    data: Optional[dict] = None
