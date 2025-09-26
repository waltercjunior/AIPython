#!/usr/bin/env python3
"""
Database initialization script.
"""
import asyncio
from app.database import create_tables


async def init_db():
    """Initialize the database."""
    print("Creating database tables...")
    await create_tables()
    print("Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
