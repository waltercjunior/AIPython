"""
Dependency injection container for the application.
"""
from typing import Generator
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from app.core.services.user_service import UserService


def get_user_repository(db: Session = None) -> UserRepository:
    """Get user repository instance."""
    if db is None:
        db = next(get_db())
    return UserRepositoryImpl(db)


def get_user_service(db: Session = None) -> UserService:
    """Get user service instance."""
    repository = get_user_repository(db)
    return UserService(repository)


def get_dependencies() -> Generator:
    """Get all dependencies."""
    db = next(get_db())
    try:
        yield {
            "db": db,
            "user_repository": get_user_repository(db),
            "user_service": get_user_service(db),
        }
    finally:
        db.close()
