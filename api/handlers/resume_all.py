"""
Consolidated resume handler.

Fetches ALL resume data from DynamoDB in a single scan, partitions by type,
and caches the result at module level for warm Lambda reuse.

Cache is cleared on Lambda cold start (i.e., redeployment).
"""
from handlers.db import get_dynamodb_table

# ---------------------------------------------------------------------------
# Module-level cache — persists across warm Lambda invocations
# ---------------------------------------------------------------------------
_cached_resume = None


def _build_cache():
    """
    Single DynamoDB scan → partition + sort → cache.
    
    Returns:
        dict with keys: profile, work_experience, education, skills
    """
    table = get_dynamodb_table()
    response = table.scan()
    items = response.get('Items', [])

    result = {
        "profile": None,
        "work_experience": [],
        "education": [],
        "skills": []
    }

    for item in items:
        item_type = item.get('type')

        if item_type == 'profile':
            # Strip DynamoDB metadata
            item.pop('id', None)
            item.pop('type', None)
            result["profile"] = item

        elif item_type == 'work_experience':
            result["work_experience"].append(item)

        elif item_type == 'education':
            result["education"].append(item)

        elif item_type == 'skills':
            result["skills"].append(item)

    # --- Sorting ---
    # Work experience: current jobs first, then by start date descending
    result["work_experience"].sort(
        key=lambda x: x.get('start_date', ''),
        reverse=True
    )
    result["work_experience"].sort(
        key=lambda x: not x.get('is_current', False)
    )

    # Education: most recent first
    result["education"].sort(
        key=lambda x: x.get('start_date', ''),
        reverse=True
    )

    # Skills: by sort_order, then category name
    result["skills"].sort(
        key=lambda x: (
            int(x.get('sort_order', 999)),
            x.get('category', '')
        )
    )

    return result


def get_all_resume_data():
    """
    Return the full resume dataset, cached after first call.
    
    Returns:
        dict: { profile, work_experience, education, skills }
    """
    global _cached_resume
    if _cached_resume is None:
        _cached_resume = _build_cache()
    return _cached_resume


def clear_cache():
    """
    Manually bust the cache if needed (e.g., from a future admin endpoint).
    """
    global _cached_resume
    _cached_resume = None
