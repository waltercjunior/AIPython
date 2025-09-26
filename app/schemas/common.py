"""
Common schemas used across the application.
"""
from typing import Optional
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str
    message: str
    details: Optional[dict] = None


class SuccessResponse(BaseModel):
    """Schema for success responses."""
    message: str
    data: Optional[dict] = None


class PaginationParams(BaseModel):
    """Schema for pagination parameters."""
    skip: int = 0
    limit: int = 100
