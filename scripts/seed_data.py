#!/usr/bin/env python3
"""
Seed data script for development.
"""
import asyncio
from app.database import get_db
from app.core.services.user_service import UserService
from app.dependencies import get_user_service


async def seed_data():
    """Seed the database with sample data."""
    print("Seeding database with sample data...")
    
    # Get database session
    db = next(get_db())
    user_service = get_user_service(db)
    
    # Create sample users
    sample_users = [
        {"name": "John Doe", "email": "john.doe@example.com"},
        {"name": "Jane Smith", "email": "jane.smith@example.com"},
        {"name": "Bob Johnson", "email": "bob.johnson@example.com"},
    ]
    
    for user_data in sample_users:
        try:
            await user_service.create_user(
                name=user_data["name"],
                email=user_data["email"]
            )
            print(f"Created user: {user_data['name']}")
        except Exception as e:
            print(f"Error creating user {user_data['name']}: {e}")
    
    print("Database seeding completed!")


if __name__ == "__main__":
    asyncio.run(seed_data())
