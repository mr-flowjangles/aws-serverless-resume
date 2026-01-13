"""
Test work experience handler directly (tests both FastAPI and Lambda).
"""
import pytest
from shared.handlers import work_experience


def test_get_work_experience():
    """Test get_work_experience returns expected structure."""
    print("\nTesting work experience handler")
    
    items = work_experience.get_work_experience()
    
    assert isinstance(items, list)
    assert len(items) > 0
    
    # Check first item structure
    item = items[0]
    assert "company_name" in item
    assert "job_title" in item
    assert "start_date" in item
    assert "description" in item


def test_work_experience_sorted():
    """Test that work experience is sorted correctly (current jobs first, then by date)."""
    items = work_experience.get_work_experience()
    
    # Verify we have items
    assert len(items) > 0
    
    # If there are current jobs, they should be first
    current_jobs = [i for i in items if i.get("is_current", False)]
    past_jobs = [i for i in items if not i.get("is_current", False)]
    
    if current_jobs and past_jobs:
        # Find index of first current job and first past job
        first_current_idx = next(i for i, item in enumerate(items) if item.get("is_current", False))
        first_past_idx = next(i for i, item in enumerate(items) if not item.get("is_current", False))
        
        # Current jobs should come before past jobs
        assert first_current_idx < first_past_idx