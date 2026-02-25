"""
Embedding Generator (Universal)

Reads a bot's data via the chunker, generates embeddings via AWS Bedrock
(Amazon Titan Text Embeddings V2), and stores them in the ChatbotRAG
DynamoDB table with a bot_id field.

Uses kill-and-fill scoped to the bot_id — only deletes and rewrites
embeddings for the specified bot. Other bots are untouched.

Behavior:
  - First run:      No embeddings found → generates automatically
  - Already exist:  Prompts "Regenerate? (y/n)" before proceeding
  - --force flag:   Skips the prompt, regenerates without asking

Usage:
    python -m ai.factory.core.generate_embeddings guitar
    python -m ai.factory.core.generate_embeddings guitar --force
"""
import os
import sys
import json
import boto3
from decimal import Decimal
from .chunker import load_bot_data


BEDROCK_MODEL_ID = "amazon.titan-embed-text-v2:0"
EMBEDDING_DIMENSIONS = 1024


# ---------------------------------------------------------------------------
# Connections
# ---------------------------------------------------------------------------

def get_dynamodb_connection():
    """Get DynamoDB connection (works with LocalStack or AWS)."""
    endpoint_url = os.getenv('AWS_ENDPOINT_URL', '')

    if endpoint_url == '':
        return boto3.resource('dynamodb', region_name='us-east-1')
    else:
        return boto3.resource(
            'dynamodb',
            endpoint_url=endpoint_url,
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
        )


def get_bedrock_client():
    """Initialize Bedrock runtime client. Always calls real AWS."""
    return boto3.client('bedrock-runtime', region_name='us-east-1')


# ---------------------------------------------------------------------------
# Embedding generation
# ---------------------------------------------------------------------------

def generate_embedding(client, text: str) -> list[float]:
    """Generate a single embedding vector via Bedrock Titan V2."""
    response = client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps({
            "inputText": text,
            "dimensions": EMBEDDING_DIMENSIONS,
            "normalize": True
        })
    )
    return json.loads(response['body'].read())['embedding']


def generate_all_embeddings(client, chunks: list[dict]) -> list[dict]:
    """Generate embeddings for all chunks. Adds 'embedding' key to each chunk."""
    print(f"\nGenerating embeddings with Bedrock Titan V2 ({len(chunks)} chunks)...")

    for idx, chunk in enumerate(chunks, 1):
        print(f"  [{idx}/{len(chunks)}] {chunk['category']}: {chunk['id']}")

        try:
            chunk['embedding'] = generate_embedding(client, chunk['text'])
        except Exception as e:
            print(f"  Error generating embedding for '{chunk['id']}': {e}")
            sys.exit(1)

    print(f"  Done — {len(chunks)} embeddings generated")
    return chunks


# ---------------------------------------------------------------------------
# DynamoDB storage
# ---------------------------------------------------------------------------

def clear_bot_embeddings(table, bot_id: str):
    """
    Delete all existing embeddings for this bot_id.
    Only removes rows where bot_id matches — other bots are untouched.
    """
    print(f"\nClearing existing embeddings for bot '{bot_id}'...")

    response = table.scan()
    items = response.get('Items', [])

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))

    bot_items = [item for item in items if item.get('bot_id') == bot_id]

    if not bot_items:
        print(f"  No existing embeddings found for '{bot_id}'")
        return

    with table.batch_writer() as batch:
        for item in bot_items:
            batch.delete_item(Key={'id': item['id']})

    print(f"  Deleted {len(bot_items)} existing embeddings")


def store_embeddings(table, chunks: list[dict]):
    """Write chunks with embeddings to DynamoDB."""
    print(f"\nStoring {len(chunks)} embeddings in ChatbotRAG...")

    with table.batch_writer() as batch:
        for chunk in chunks:
            item = {
                'id': f"{chunk['bot_id']}_{chunk['id']}",
                'bot_id': chunk['bot_id'],
                'category': chunk['category'],
                'heading': chunk['heading'],
                'text': chunk['text'],
                'embedding': [Decimal(str(x)) for x in chunk['embedding']],
            }
            batch.put_item(Item=item)

    print(f"  Done — {len(chunks)} embeddings stored")


# ---------------------------------------------------------------------------
# Check if embeddings exist
# ---------------------------------------------------------------------------

def bot_embeddings_exist(table, bot_id: str) -> bool:
    """Check if this bot already has embeddings in the table."""
    response = table.scan()
    items = response.get('Items', [])

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))

    return any(item.get('bot_id') == bot_id for item in items)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate_bot_embeddings(bot_id: str, force: bool = False):
    """
    Full pipeline: chunker → Bedrock Titan V2 → DynamoDB for a given bot.

    Args:
        bot_id: The bot folder name (e.g., 'guitar')
        force:  If True, regenerate even if embeddings already exist
    """
    print("\n" + "=" * 60)
    print(f"  Bot Factory — Embedding Generator")
    print(f"  Bot: {bot_id}")
    print(f"  Model: {BEDROCK_MODEL_ID} ({EMBEDDING_DIMENSIONS}d)")
    print("=" * 60 + "\n")

    # Step 1: Connect to DynamoDB
    dynamodb = get_dynamodb_connection()
    table = dynamodb.Table('ChatbotRAG')

    # Step 2: Check if embeddings already exist
    if bot_embeddings_exist(table, bot_id):
        if not force:
            answer = input(f"Embeddings already exist for '{bot_id}'. Regenerate? (y/n): ").strip().lower()
            if answer != 'y':
                print("  Skipping — existing embeddings unchanged.")
                return
        print(f"  Regenerating embeddings for '{bot_id}'...")

    # Step 3: Load and chunk the bot's data
    chunks = load_bot_data(bot_id)

    if not chunks:
        print(f"No data found for bot '{bot_id}'. Check bots/{bot_id}/data/")
        sys.exit(1)

    # Step 4: Generate embeddings via Bedrock
    bedrock_client = get_bedrock_client()
    chunks = generate_all_embeddings(bedrock_client, chunks)

    # Step 5: Clear old embeddings for this bot (kill-and-fill, scoped)
    clear_bot_embeddings(table, bot_id)

    # Step 6: Store new embeddings
    store_embeddings(table, chunks)

    # Summary
    from collections import Counter
    cats = Counter(c['category'] for c in chunks)

    print("\n" + "=" * 60)
    print(f"  Embeddings generation complete!")
    print("=" * 60)
    print(f"\n  Bot: {bot_id}")
    print(f"  Model: {BEDROCK_MODEL_ID}")
    print(f"  Dimensions: {EMBEDDING_DIMENSIONS}")
    print(f"  Total embeddings: {len(chunks)}")
    for cat, count in cats.most_common():
        print(f"    {cat}: {count}")
    print(f"  Stored in: ChatbotRAG table (bot_id='{bot_id}')")
    print()


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m ai.factory.core.generate_embeddings <bot_id> [--force]")
        print("Example: python -m ai.factory.core.generate_embeddings guitar")
        sys.exit(1)

    bot_id = sys.argv[1]
    force = '--force' in sys.argv

    generate_bot_embeddings(bot_id, force=force)


if __name__ == '__main__':
    main()
