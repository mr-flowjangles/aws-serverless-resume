#!/usr/bin/env python3
"""
Import embeddings to AWS production DynamoDB, scoped by bot_id.
Does a kill-and-fill: deletes existing rows for the bot, then writes new ones.

Always targets prod AWS. Uses your host machine's AWS credentials.

Usage:
    python3 ai/scripts/import_embeddings.py guitar
    python3 ai/scripts/import_embeddings.py robbai
    python3 ai/scripts/import_embeddings.py --all
"""
import boto3
import json
import os
import sys
from decimal import Decimal


def convert_floats_to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(i) for i in obj]
    return obj


def import_embeddings(bot_id=None):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    # Determine input file
    if bot_id:
        input_path = f'_scratch/{bot_id}-embeddings-export.json'
    else:
        input_path = '_scratch/embeddings-export.json'

    if not os.path.exists(input_path):
        print(f'Error: {input_path} not found')
        print('Run export_embeddings.py first')
        sys.exit(1)

    with open(input_path, 'r') as f:
        items = json.load(f)

    if not items:
        print(f'No items found in {input_path}')
        sys.exit(1)

    items = convert_floats_to_decimal(items)

    table = dynamodb.Table('ChatbotRAG')

    # Kill: delete existing rows for this bot (or all if --all)
    if bot_id:
        print(f"Deleting existing '{bot_id}' embeddings from prod...")
        scan_kwargs = {
            'FilterExpression': 'bot_id = :bid',
            'ExpressionAttributeValues': {':bid': bot_id},
            'ProjectionExpression': 'id'
        }
    else:
        print("Deleting ALL existing embeddings from prod...")
        scan_kwargs = {'ProjectionExpression': 'id'}

    existing = []
    response = table.scan(**scan_kwargs)
    existing.extend(response.get('Items', []))

    while 'LastEvaluatedKey' in response:
        scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
        response = table.scan(**scan_kwargs)
        existing.extend(response.get('Items', []))

    if existing:
        with table.batch_writer() as batch:
            for item in existing:
                batch.delete_item(Key={'id': item['id']})
        print(f'Deleted {len(existing)} existing rows')

    # Fill: write new rows
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)

    label = f"'{bot_id}'" if bot_id else "all bots"
    print(f'Imported {len(items)} embeddings ({label}) to prod ChatbotRAG')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python import_embeddings.py <bot_id>    Import one bot (kill-and-fill)")
        print("  python import_embeddings.py --all       Import all bots (kill-and-fill)")
        sys.exit(1)

    arg = sys.argv[1]
    if arg == '--all':
        import_embeddings(bot_id=None)
    else:
        import_embeddings(bot_id=arg)
