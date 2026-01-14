"""
Test skills handler directly (tests both FastAPI and Lambda).
"""
import pytest
from handlers import skills


def test_get_skills():
    """Test get_skills returns expected structure."""
    print("\nTesting skills handler")
    
    items = skills.get_skills()
    
    assert isinstance(items, list)
    assert len(items) > 0
    
    # Check first item structure
    item = items[0]
    assert "category" in item
    assert "skills" in item
    assert isinstance(item["skills"], list)


def test_skills_sorted():
    """Test that skills are sorted by sort_order or category name."""
    items = skills.get_skills()
    
    # Verify sorting logic
    for i in range(len(items) - 1):
        current_order = items[i].get("sort_order", 999)
        next_order = items[i + 1].get("sort_order", 999)
        
        if current_order == next_order:
            # If sort_order is same, should be sorted by category
            assert items[i].get("category", "") <= items[i + 1].get("category", "")
        else:
            assert current_order <= next_order
