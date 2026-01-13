"""
Lambda function for /resume/profile endpoint.
Uses shared handler logic from shared.handlers.
"""
import json
import sys
sys.path.insert(0, '/opt/python')  # Lambda layer path

from shared.handlers import profile as profile_handler


def lambda_handler(event, context):
    """Get profile from DynamoDB."""
    try:
        data = profile_handler.get_profile()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(data)
        }
        
    except ValueError as e:
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'detail': str(e)})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'detail': f'Error loading profile: {str(e)}'})
        }
