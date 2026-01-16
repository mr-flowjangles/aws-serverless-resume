"""
FastAPI router for health check endpoint.
Uses handler logic from handlers.
"""
from fastapi import APIRouter, HTTPException
from handlers import health

router = APIRouter()


@router.get("/health")
def health_check_endpoint():
    """Health check endpoint to verify DynamoDB connectivity."""
    result = health.health_check()
    
    if result["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=result)
    
    return result
