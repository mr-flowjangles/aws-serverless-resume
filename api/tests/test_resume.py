"""
Test resume handler directly (tests both FastAPI and Lambda).
"""
import pytest
from handlers.resume_all import get_all_resume_data, clear_cache


@pytest.fixture(autouse=True)
def fresh_cache():
    """Clear cache before each test so we get fresh data."""
    clear_cache()
    yield
    clear_cache()


def test_resume_returns_dict():
    """Test resume returns expected top-level structure."""
    print("\nTesting resume handler")

    result = get_all_resume_data()

    assert isinstance(result, dict)
    assert "profile" in result
    assert "work_experience" in result
    assert "education" in result
    assert "skills" in result


def test_profile_structure():
    """Test profile has required fields."""
    result = get_all_resume_data()
    profile = result["profile"]

    assert profile is not None
    assert "name" in profile
    assert "title" in profile


def test_work_experience_is_list():
    """Test work experience returns a sorted list."""
    result = get_all_resume_data()
    items = result["work_experience"]

    assert isinstance(items, list)
    assert len(items) > 0


def test_work_experience_sorted():
    """Test current jobs appear before past jobs."""
    result = get_all_resume_data()
    items = result["work_experience"]

    # Find first non-current job
    found_past = False
    for item in items:
        if not item.get("is_current", False):
            found_past = True
        if found_past and item.get("is_current", False):
            pytest.fail("Current job found after past job — sorting is wrong")


def test_education_is_list():
    """Test education returns a list."""
    result = get_all_resume_data()
    items = result["education"]

    assert isinstance(items, list)
    assert len(items) > 0


def test_skills_is_list():
    """Test skills returns a list."""
    result = get_all_resume_data()
    items = result["skills"]

    assert isinstance(items, list)
    assert len(items) > 0


def test_cache_returns_same_object():
    """Test that repeated calls return the same cached data."""
    first = get_all_resume_data()
    second = get_all_resume_data()

    assert first is second
