#!/usr/bin/env python3
"""
Export embeddings from LocalStack to JSON file.
Run from project root: docker compose exec api python /app/ai/scripts/export_embeddings.py
"""
import boto3
import json
import os
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)


def export_embeddings():
    endpoint_url = os.getenv('AWS_ENDPOINT_URL', 'http://localstack:4566')
    
    if endpoint_url == "":
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        print("Exporting from AWS production...")
    else:
        dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=endpoint_url,
            region_name='us-east-1',
            aws_access_key_id='test',
            aws_secret_access_key='test'
        )
        print("Exporting from LocalStack...")
    
    table = dynamodb.Table('ChatbotRAG')
    response = table.scan()
    items = response['Items']
    
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])
    
    output_path = '/app/_scratch/embeddings-export.json'
    with open(output_path, 'w') as f:
        json.dump(items, f, cls=DecimalEncoder)
    
    print(f'Exported {len(items)} embeddings to {output_path}')


if __name__ == '__main__':
    export_embeddings()
