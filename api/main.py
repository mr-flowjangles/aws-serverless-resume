from contextlib import asynccontextmanager
from fastapi import FastAPI
from chat import router as chat_router
from health import router as health_router
from resume import router as resume_router
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
app.include_router(chat_router)
app.include_router(health_router)
app.include_router(resume_router)

@app.get("/hello")
def hello():
    """Simple hello endpoint for testing"""
    return {"message": "hello from fastAPI, sup dog"}