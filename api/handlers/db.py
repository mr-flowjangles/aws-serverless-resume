"""
DynamoDB connection helper.
Provides functions to get DynamoDB table and client for handlers.
"""
import os
import boto3


def get_dynamodb_table():
    """
    Get DynamoDB table resource.
    
    Returns:
        boto3.resource.Table: DynamoDB table
    """
    # Check if running in LocalStack (local development)
    endpoint_url = os.getenv('AWS_ENDPOINT_URL')
    
    if endpoint_url:
        # LocalStack
        dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=endpoint_url,
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
            aws_access_key_id='test',
            aws_secret_access_key='test'
        )
    else:
        # Real AWS
        dynamodb = boto3.resource(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
    
    table_name = os.getenv('DYNAMODB_TABLE', 'ResumeData')
    return dynamodb.Table(table_name)


def get_dynamodb_client():
    """
    Get DynamoDB client.
    
    Returns:
        boto3.client: DynamoDB client
    """
    # Check if running in LocalStack (local development)
    endpoint_url = os.getenv('AWS_ENDPOINT_URL')
    
    if endpoint_url:
        # LocalStack
        return boto3.client(
            'dynamodb',
            endpoint_url=endpoint_url,
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
            aws_access_key_id='test',
            aws_secret_access_key='test'
        )
    else:
        # Real AWS
        return boto3.client(
            'dynamodb',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
