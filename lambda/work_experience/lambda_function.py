"""
Lambda function for /resume/work-experience endpoint
"""
import boto3
import json
import os

def lambda_handler(event, context):
    """
    Get work experience items sorted by date (most recent first).
    
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
        
        # Query work experience items
        response = table.query(
            IndexName='TypeIndex',
            KeyConditionExpression='#t = :type',
            ExpressionAttributeNames={'#t': 'type'},
            ExpressionAttributeValues={':type': 'work_experience'}
        )
        
        items = response.get('Items', [])
        
        # Sort: current jobs first, then by start date descending
        items.sort(key=lambda x: (
            not x.get('is_current', False),  # Current jobs first
            x.get('start_date', '')
        ), reverse=True)
        
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
            'body': json.dumps({'detail': f'Error loading work experience: {str(e)}'})
        }
