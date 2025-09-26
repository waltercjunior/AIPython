"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1 import users, auth
from app.config import settings
from app.database import create_tables
from app.middleware import LoggingMiddleware


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.APP_VERSION,
        description="A modern Python web API project using FastAPI with clean architecture",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    app.add_middleware(LoggingMiddleware)

    # Include routers
    app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
    app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])

    @app.on_event("startup")
    async def startup_event():
        """Initialize application on startup."""
        await create_tables()

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Welcome to AIPython API",
            "version": settings.APP_VERSION,
            "docs": "/docs"
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "environment": settings.ENVIRONMENT}

    return app


# Create the app instance
app = create_app()
