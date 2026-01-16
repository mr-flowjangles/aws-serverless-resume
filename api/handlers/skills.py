"""
Shared skills handler logic.
"""
from handlers.db import get_dynamodb_table

def get_skills():
    """
    Get skills organized by category.
    
    Returns:
        list: Skills items
    """
    table = get_dynamodb_table()
    
    response = table.query(
        IndexName='TypeIndex',
        KeyConditionExpression='#t = :type',
        ExpressionAttributeNames={'#t': 'type'},
        ExpressionAttributeValues={':type': 'skills'}
    )
    
    items = response.get('Items', [])
    
    # Sort by sort_order if present, otherwise by category name
    items.sort(key=lambda x: (
        x.get('sort_order', 999),
        x.get('category', '')
    ))
    
    return items
