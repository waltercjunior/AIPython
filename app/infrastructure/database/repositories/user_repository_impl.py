"""
Repository implementations for data access.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.entities.user import User
from app.core.repositories.user_repository import UserRepository
from app.infrastructure.database.models import UserModel


class UserRepositoryImpl(UserRepository):
    """SQLAlchemy implementation of UserRepository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, user: User) -> User:
        """Create a new user."""
        db_user = UserModel(
            name=user.name,
            email=user.email,
            is_active=user.is_active
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return self._to_entity(db_user)
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(db_user) if db_user else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        return self._to_entity(db_user) if db_user else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        db_users = (
            self.db.query(UserModel)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._to_entity(db_user) for db_user in db_users]
    
    async def update(self, user: User) -> User:
        """Update user."""
        db_user = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        if db_user:
            db_user.name = user.name
            db_user.email = user.email
            db_user.is_active = user.is_active
            self.db.commit()
            self.db.refresh(db_user)
            return self._to_entity(db_user)
        return user
    
    async def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False
    
    async def exists(self, user_id: int) -> bool:
        """Check if user exists."""
        return self.db.query(UserModel).filter(UserModel.id == user_id).first() is not None
    
    def _to_entity(self, db_user: UserModel) -> User:
        """Convert database model to domain entity."""
        return User(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
