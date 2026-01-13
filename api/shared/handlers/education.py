"""
Shared education handler logic.
"""
from shared.db import get_dynamodb_table

def get_education():
    """
    Get education items sorted by date (most recent first).
    
    Returns:
        list: Education items
    """
    table = get_dynamodb_table()
    
    response = table.query(
        IndexName='TypeIndex',
        KeyConditionExpression='#t = :type',
        ExpressionAttributeNames={'#t': 'type'},
        ExpressionAttributeValues={':type': 'education'}
    )
    
    items = response.get('Items', [])
    
    # Sort by start date descending
    items.sort(key=lambda x: x.get('start_date', ''), reverse=True)
    
    return items
