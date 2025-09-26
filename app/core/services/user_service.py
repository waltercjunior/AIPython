"""
Business services layer.
"""
from typing import List, Optional

from app.core.entities.user import User
from app.core.repositories.user_repository import UserRepository
from app.exceptions import NotFoundError, ConflictError


class UserService:
    """User business logic service."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def create_user(self, name: str, email: str) -> User:
        """Create a new user with business logic validation."""
        
        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise ConflictError(f"User with email {email} already exists")
        
        # Create new user
        user = User(name=name, email=email)
        return await self.user_repository.create(user)
    
    async def get_user(self, user_id: int) -> User:
        """Get user by ID."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return await self.user_repository.get_by_email(email)
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        return await self.user_repository.get_all(skip=skip, limit=limit)
    
    async def update_user(self, user_id: int, **kwargs) -> User:
        """Update user with business logic validation."""
        
        # Get existing user
        user = await self.get_user(user_id)
        
        # Check email uniqueness if email is being updated
        if "email" in kwargs and kwargs["email"] != user.email:
            existing_user = await self.user_repository.get_by_email(kwargs["email"])
            if existing_user:
                raise ConflictError(f"User with email {kwargs['email']} already exists")
        
        # Update user
        user.update(**kwargs)
        return await self.user_repository.update(user)
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete user."""
        
        # Check if user exists
        if not await self.user_repository.exists(user_id):
            raise NotFoundError(f"User with ID {user_id} not found")
        
        return await self.user_repository.delete(user_id)
    
    async def activate_user(self, user_id: int) -> User:
        """Activate user."""
        user = await self.get_user(user_id)
        user.activate()
        return await self.user_repository.update(user)
    
    async def deactivate_user(self, user_id: int) -> User:
        """Deactivate user."""
        user = await self.get_user(user_id)
        user.deactivate()
        return await self.user_repository.update(user)
