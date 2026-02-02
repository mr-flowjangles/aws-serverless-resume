#!/usr/bin/env python3
"""
Import embeddings from JSON file to AWS DynamoDB.
Run from project root: AWS_ENDPOINT_URL="" python3 ai/scripts/import_embeddings.py
"""
import boto3
import json
import os
from decimal import Decimal


def convert_floats_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(i) for i in obj]
    return obj


def import_embeddings():
    endpoint_url = os.getenv('AWS_ENDPOINT_URL', '')
    
    if endpoint_url == "":
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        print("Importing to AWS production...")
    else:
        dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=endpoint_url,
            region_name='us-east-1',
            aws_access_key_id='test',
            aws_secret_access_key='test'
        )
        print("Importing to LocalStack...")
    
    input_path = '_scratch/embeddings-export.json'
    
    if not os.path.exists(input_path):
        print(f'Error: {input_path} not found')
        print('Run export_embeddings.py first')
        return
    
    with open(input_path, 'r') as f:
        items = json.load(f)
    
    items = convert_floats_to_decimal(items)
    
    table = dynamodb.Table('ChatbotRAG')
    
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)
    
    print(f'Imported {len(items)} embeddings to ChatbotRAG')


if __name__ == '__main__':
    import_embeddings()
