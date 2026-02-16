#!/usr/bin/env python3
"""
Export embeddings from LocalStack to JSON file.
Run from project root: docker compose exec api python /app/ai/scripts/export_embeddings.py guitar
"""
import boto3
import json
import os
import sys
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)


def export_embeddings(bot_id):
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
    
    scan_kwargs = {
        'FilterExpression': 'bot_id = :bid',
        'ExpressionAttributeValues': {':bid': bot_id}
    }
    
    response = table.scan(**scan_kwargs)
    items = response['Items']
    
    while 'LastEvaluatedKey' in response:
        scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
        response = table.scan(**scan_kwargs)
        items.extend(response['Items'])
    
    output_path = f'_scratch/{bot_id}-embeddings-export.json'
    with open(output_path, 'w') as f:
        json.dump(items, f, cls=DecimalEncoder)
    
    print(f'Exported {len(items)} embeddings to {output_path}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python export_embeddings.py <bot_id>")
        sys.exit(1)
    export_embeddings(sys.argv[1])