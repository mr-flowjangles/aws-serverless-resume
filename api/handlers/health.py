"""
Shared health check handler logic.
"""
from handlers.db import get_dynamodb_client
from ai.retrieval import get_cached_embeddings

def health_check():
    """
    Health check to verify DynamoDB connectivity and pre-load embeddings cache.
    
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
    
    # Pre-load embeddings cache (cold start optimization)
    try:
        embeddings = get_cached_embeddings()
        health_status["services"]["embeddings_cache"] = f"ok ({len(embeddings)} loaded)"
    except Exception as e:
        health_status["services"]["embeddings_cache"] = f"error: {str(e)}"
        # Don't mark as unhealthy - cache can be loaded on first request
    
    return health_status
