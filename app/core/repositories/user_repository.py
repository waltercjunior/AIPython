"""
Repository interfaces for data access abstraction.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.core.entities.user import User


class UserRepository(ABC):
    """Abstract user repository interface."""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        pass
    
    @abstractmethod
    async def exists(self, user_id: int) -> bool:
        """Check if user exists."""
        pass
