"""
Test education handler directly (tests both FastAPI and Lambda).
"""
import pytest
from handlers import education


def test_get_education():
    """Test get_education returns expected structure."""
    print("\nTesting education handler")
    
    items = education.get_education()
    
    assert isinstance(items, list)
    assert len(items) > 0
    
    # Check first item structure
    item = items[0]
    assert "institution" in item
    assert "degree" in item
    assert "start_date" in item
    assert "end_date" in item


def test_education_sorted_by_date():
    """Test that education items are sorted by date (most recent first)."""
    items = education.get_education()
    
    if len(items) > 1:
        # Check that dates are in descending order
        dates = [i.get("start_date", "") for i in items]
        assert dates == sorted(dates, reverse=True)
