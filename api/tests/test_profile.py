"""
Test profile handler directly (tests both FastAPI and Lambda).
"""
import pytest
from handlers import profile


def test_get_profile():
    """Test get_profile returns all expected fields."""
    print("\nTesting profile handler for all expected fields")
    
    data = profile.get_profile()
    
    assert isinstance(data, dict)
    assert "name" in data
    assert "title" in data
    assert "email" in data
    assert "location" in data
    assert "summary" in data
    assert "github" in data
    assert "linkedin" in data
    
    # Verify data types
    assert isinstance(data["name"], str)
    assert isinstance(data["email"], str)
    assert len(data["name"]) > 0


def test_get_profile_no_metadata():
    """Test that DynamoDB metadata fields are removed."""
    data = profile.get_profile()
    
    # These should NOT be in the response
    assert "id" not in data
    assert "type" not in data
