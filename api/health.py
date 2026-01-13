"""
FastAPI router for health check endpoint.
Uses shared handler logic from shared.handlers.
"""
from fastapi import APIRouter, HTTPException
from shared.handlers import health

router = APIRouter()


@router.get("/health")
def health_check_endpoint():
    """Health check endpoint to verify DynamoDB connectivity."""
    result = health.health_check()
    
    if result["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=result)
    
    return result
