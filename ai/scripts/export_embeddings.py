#!/usr/bin/env python3
"""
Export embeddings from LocalStack to JSON file, scoped by bot_id.

Usage:
    docker compose exec api python /app/ai/scripts/export_embeddings.py guitar
    docker compose exec api python /app/ai/scripts/export_embeddings.py robbai
    docker compose exec api python /app/ai/scripts/export_embeddings.py --all
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


def export_embeddings(bot_id=None):
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

    # Filter by bot_id if specified, otherwise export all
    if bot_id:
        scan_kwargs = {
            'FilterExpression': 'bot_id = :bid',
            'ExpressionAttributeValues': {':bid': bot_id}
        }
    else:
        scan_kwargs = {}

    response = table.scan(**scan_kwargs)
    items = response['Items']

    while 'LastEvaluatedKey' in response:
        scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
        response = table.scan(**scan_kwargs)
        items.extend(response['Items'])

    if bot_id:
        output_path = f'_scratch/{bot_id}-embeddings-export.json'
        label = f"'{bot_id}'"
    else:
        output_path = '_scratch/embeddings-export.json'
        label = "all bots"

    with open(output_path, 'w') as f:
        json.dump(items, f, cls=DecimalEncoder)

    print(f'Exported {len(items)} embeddings ({label}) to {output_path}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python export_embeddings.py <bot_id>    Export one bot")
        print("  python export_embeddings.py --all       Export all bots")
        sys.exit(1)

    arg = sys.argv[1]
    if arg == '--all':
        export_embeddings(bot_id=None)
    else:
        export_embeddings(bot_id=arg)
