"""
Shared profile handler logic.
"""
from handlers.db import get_dynamodb_table

def get_profile():
    """
    Get profile from DynamoDB.
    
    Returns:
        dict: Profile data
        
    Raises:
        ValueError: If profile not found
        Exception: For other errors
    """
    table = get_dynamodb_table()
    
    response = table.get_item(Key={'id': 'profile'})
    
    if 'Item' not in response:
        raise ValueError('Profile not found')
    
    # Remove DynamoDB metadata
    item = response['Item']
    item.pop('id', None)
    item.pop('type', None)
    
    return item
