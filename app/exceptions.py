"""
Custom exceptions for the application.
"""
from typing import Any, Dict, Optional


class BaseAPIException(Exception):
    """Base exception for API errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseAPIException):
    """Validation error exception."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 422, details)


class NotFoundError(BaseAPIException):
    """Not found error exception."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


class ConflictError(BaseAPIException):
    """Conflict error exception."""
    
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, 409)


class UnauthorizedError(BaseAPIException):
    """Unauthorized error exception."""
    
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401)


class ForbiddenError(BaseAPIException):
    """Forbidden error exception."""
    
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, 403)


class InternalServerError(BaseAPIException):
    """Internal server error exception."""
    
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, 500)
