"""
Shared work experience handler logic.
"""
from shared.db import get_dynamodb_table

def get_work_experience():
    """
    Get work experience items sorted by date (most recent first).
    
    Returns:
        list: Work experience items
    """
    table = get_dynamodb_table()
    
    response = table.query(
        IndexName='TypeIndex',
        KeyConditionExpression='#t = :type',
        ExpressionAttributeNames={'#t': 'type'},
        ExpressionAttributeValues={':type': 'work_experience'}
    )
    
    items = response.get('Items', [])
    
    # Sort: current jobs first, then past jobs
    # Within each group, sort by start date descending (most recent first)
    items.sort(
        key=lambda x: (
            0 if x.get('is_current', False) else 1,  # Current = 0 (first), Past = 1 (second)
            x.get('start_date', '')  # Date in ascending order
        ),
        reverse=False  
    )
    
    # Now reverse just the dates within each group
    # Separate into current and past
    current = [x for x in items if x.get('is_current', False)]
    past = [x for x in items if not x.get('is_current', False)]
    
    # Reverse each group to get most recent first
    current.reverse()
    past.reverse()
    
    # Combine: current jobs first, then past jobs
    return current + past