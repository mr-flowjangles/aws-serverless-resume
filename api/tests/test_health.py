"""
Test health check handler directly (tests both FastAPI and Lambda).
"""
import pytest
from shared.handlers import health


def test_health_check():
    """Test health check returns expected structure."""
    print("\nTesting health check handler")
    
    result = health.health_check()
    
    assert isinstance(result, dict)
    assert "status" in result
    assert "services" in result
    assert isinstance(result["services"], dict)
    
    # Check DynamoDB service status
    assert "dynamodb" in result["services"]


def test_health_check_status():
    """Test that health check returns correct status."""
    result = health.health_check()
    
    # Status should be either "healthy" or "unhealthy"
    assert result["status"] in ["healthy", "unhealthy"]
    
    # If DynamoDB is ok, overall status should be healthy
    if result["services"]["dynamodb"] == "ok":
        assert result["status"] == "healthy"
