"""
FastAPI application for AWS Serverless Resume.

Serves resume data from DynamoDB with endpoints for profile, work experience,
education, skills, and contact form. Auto-seeds database from Excel on startup.

This module manages the routers that are exposed as endpoints under /api.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers.health import router as health_router
from routers.contact import router as contact_router
from routers.resume import router as resume_router
from ai.router import router as ai_router
from fastapi.middleware.cors import CORSMiddleware
from ai.factory import factory_router



@asynccontextmanager
async def lifespan(app):
    """
    Application lifespan manager
    Runs code on startup and shutdown
    """
    # Startup: Seed database if empty
    if 'localhost' in os.getenv('AWS_ENDPOINT_URL', '') or 'localstack' in os.getenv('AWS_ENDPOINT_URL', ''):
        from seed import seed_database
        seed_database()
    yield
    # Shutdown: cleanup code here if needed


# Initialize FastAPI app with lifespan and API prefix
app = FastAPI(
    servers=[{"url": "/api"}],
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://robrose.info", "https://www.robrose.info", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Detect if running in Lambda (adds /api prefix only in Lambda)
# Locally, Nginx already adds /api, so we don't need the prefix
is_lambda = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None
prefix = "/api" if is_lambda else ""

# Include routers for different API sections, chatbots, etc
app.include_router(health_router, prefix=prefix)
app.include_router(resume_router, prefix=prefix)
app.include_router(contact_router, prefix=prefix)
app.include_router(ai_router, prefix=prefix)
app.include_router(factory_router, prefix=prefix)