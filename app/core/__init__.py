"""
Core domain entities.
"""
from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class User:
    """User domain entity."""
    
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def update(self, **kwargs):
        """Update user fields."""
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
    
    def activate(self):
        """Activate user."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def deactivate(self):
        """Deactivate user."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
