"""
Lambda function for /health endpoint
"""
import boto3
import json
import os

def lambda_handler(event, context):
    """
    Health check endpoint to verify DynamoDB connectivity.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    health_status = {
        "status": "healthy",
        "services": {}
    }
    
    try:
        # Check DynamoDB
        dynamodb = boto3.client('dynamodb')
        dynamodb.list_tables()
        health_status["services"]["dynamodb"] = "ok"
    except Exception as e:
        health_status["services"]["dynamodb"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(health_status)
    }
