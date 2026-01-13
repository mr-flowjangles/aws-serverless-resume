"""
Lambda function for /resume/skills endpoint
"""
import boto3
import json
import os

def lambda_handler(event, context):
    """
    Get skills organized by category.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    try:
        # Get DynamoDB table
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'ResumeData'))
        
        # Query skills items
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
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'items': items})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'detail': f'Error loading skills: {str(e)}'})
        }
