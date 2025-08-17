"""
Task Management System - FastAPI Application

This module contains the main FastAPI application that provides a REST API
for managing tasks and users. The application handles database initialization,
API endpoints, and lifecycle management.

Key Components:
- FastAPI application instance with lifespan management
- Database table creation on startup
- Health check endpoint for monitoring
- Automatic database initialization

Dependencies:
- FastAPI: Web framework for building APIs
- SQLAlchemy: Database ORM and engine
- Custom models: User and Task database models
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import Base, engine  # ensures DB engine is ready
from . import models  # ensure models are imported so tables exist


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager that handles startup and shutdown events.

    This function runs once when the application starts up and handles
    any necessary initialization and cleanup operations.

    Args:
        app (FastAPI): The FastAPI application instance

    Yields:
        None: Control is yielded to the application during its runtime

    Note:
        - Startup: Creates all database tables if they don't exist
        - Shutdown: Currently no teardown operations needed
    """
    # Startup: Create all database tables based on model definitions
    # This ensures the database schema is ready before handling requests
    Base.metadata.create_all(bind=engine)

    # Yield control to the application during its runtime
    yield

    # Shutdown: Cleanup operations (none needed for now)
    # Future cleanup operations like closing connections can be added here


# Create the FastAPI application instance
# title: Human-readable name for the API
# version: API version for tracking changes
# lifespan: Function to manage application lifecycle
app = FastAPI(title="Todo API", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health():
    """
    Health check endpoint for monitoring application status.

    This endpoint is commonly used by load balancers, monitoring tools,
    and health check systems to verify the application is running.

    Returns:
        dict: Simple status response indicating the API is operational

    Example Response:
        {"status": "ok"}
    """
    return {"status": "ok"}
