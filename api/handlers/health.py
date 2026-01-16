"""
Shared health check handler logic.
"""
from handlers.db import get_dynamodb_client

def health_check():
    """
    Health check to verify DynamoDB connectivity.
    
    Returns:
        dict: Health status
    """
    health_status = {
        "status": "healthy",
        "services": {}
    }
    
    try:
        dynamodb = get_dynamodb_client()
        dynamodb.list_tables()
        health_status["services"]["dynamodb"] = "ok"
    except Exception as e:
        health_status["services"]["dynamodb"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status
