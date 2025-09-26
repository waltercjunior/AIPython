"""
API routes for the application.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_user_service
from app.core.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.schemas.common import SuccessResponse
from app.exceptions import BaseAPIException


router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """Create a new user."""
    try:
        user = await user_service.create_user(
            name=user_data.name,
            email=user_data.email
        )
        return UserResponse.from_orm(user)
    except BaseAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/", response_model=UserListResponse)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service)
):
    """Get all users with pagination."""
    users = await user_service.get_users(skip=skip, limit=limit)
    return UserListResponse(
        users=[UserResponse.from_orm(user) for user in users],
        total=len(users),
        skip=skip,
        limit=limit
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Get user by ID."""
    try:
        user = await user_service.get_user(user_id)
        return UserResponse.from_orm(user)
    except BaseAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service)
):
    """Update user."""
    try:
        update_data = user_data.dict(exclude_unset=True)
        user = await user_service.update_user(user_id, **update_data)
        return UserResponse.from_orm(user)
    except BaseAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Delete user."""
    try:
        await user_service.delete_user(user_id)
        return SuccessResponse(message=f"User {user_id} deleted successfully")
    except BaseAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Activate user."""
    try:
        user = await user_service.activate_user(user_id)
        return UserResponse.from_orm(user)
    except BaseAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Deactivate user."""
    try:
        user = await user_service.deactivate_user(user_id)
        return UserResponse.from_orm(user)
    except BaseAPIException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
