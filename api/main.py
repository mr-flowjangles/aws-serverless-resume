"""
FastAPI application for AWS Serverless Resume.

Serves resume data from DynamoDB with endpoints for profile, work experience,
education, skills, and contact form. Auto-seeds database from Excel on startup.

This module manages the routers that are exposed as endpoints under /api.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers.health import router as health_router
from routers.resume import router as resume_router
from routers.contact import router as contact_router
from seed import seed_database


@asynccontextmanager
async def lifespan(app):
    """
    Application lifespan manager
    Runs code on startup and shutdown
    """
    # Startup: Seed database if empty
    seed_database()
    yield
    # Shutdown: cleanup code here if needed


# Initialize FastAPI app with lifespan and API prefix
app = FastAPI(
    servers=[{"url": "/api"}],
    lifespan=lifespan
)

# Include routers for different API sections
app.include_router(health_router)
app.include_router(resume_router)
app.include_router(contact_router)
