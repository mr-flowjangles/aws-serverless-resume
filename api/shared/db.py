"""
Shared DynamoDB helper module.
"""
import boto3
import os

def get_dynamodb_table(table_name='ResumeData'):
    """
    Get DynamoDB table connection.
    
    Args:
        table_name: Name of the DynamoDB table
        
    Returns:
        boto3 DynamoDB Table resource
    """
    dynamodb = boto3.resource(
        'dynamodb',
        endpoint_url=os.getenv('AWS_ENDPOINT_URL'),  # None for AWS, set for LocalStack
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    return dynamodb.Table(table_name)


def get_dynamodb_client():
    """
    Get DynamoDB client connection.
    
    Returns:
        boto3 DynamoDB client
    """
    return boto3.client(
        'dynamodb',
        endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
