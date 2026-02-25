"""
Chunker Module

Reads YAML files in the universal bot data format and produces
text chunks ready for embedding generation.

Handles two format types:
  - "text": content is already readable text, pass through as-is
  - "structured": apply the template string to each item to produce text

Supports optional 'search_terms' field to improve semantic search matching.

Input:  bot_id string (resolves to s3://bot-factory-data/bots/{bot_id}/data/)
Output: List of dicts with {id, bot_id, category, heading, text}
"""
import os
import yaml
import boto3


S3_BUCKET = os.getenv('BOT_DATA_BUCKET', 'bot-factory-data')
S3_PREFIX = 'bots'


# ---------------------------------------------------------------------------
# S3 connection
# ---------------------------------------------------------------------------

def get_s3_client():
    """Get S3 client (works with LocalStack or AWS)."""
    endpoint_url = os.getenv('AWS_ENDPOINT_URL', '')

    if endpoint_url == '':
        return boto3.client('s3', region_name='us-east-1')
    else:
        return boto3.client(
            's3',
            endpoint_url=endpoint_url,
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
        )


# ---------------------------------------------------------------------------
# S3 file loading
# ---------------------------------------------------------------------------

def load_yaml_files(bot_id: str) -> list[dict]:
    """
    Load all .yml files from S3 for a bot's data folder.
    s3://bot-factory-data/bots/{bot_id}/data/*.yml
    Returns the combined list of entries from all files.
    """
    s3 = get_s3_client()
    prefix = f"{S3_PREFIX}/{bot_id}/data/"
    all_entries = []

    response = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
    objects = response.get('Contents', [])

    yml_keys = sorted(
        obj['Key'] for obj in objects
        if obj['Key'].endswith('.yml') or obj['Key'].endswith('.yaml')
    )

    if not yml_keys:
        print(f"  Warning: no .yml files found at s3://{S3_BUCKET}/{prefix}")
        return all_entries

    for key in yml_keys:
        filename = key.split('/')[-1]
        print(f"  Reading s3://{S3_BUCKET}/{key}...")

        obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
        data = yaml.safe_load(obj['Body'].read().decode('utf-8'))

        entries = data.get('entries', [])
        all_entries.extend(entries)
        print(f"    Found {len(entries)} entries")

    return all_entries


# ---------------------------------------------------------------------------
# Chunking logic (unchanged)
# ---------------------------------------------------------------------------

def chunk_text_entry(entry: dict) -> str:
    """
    Process a 'text' format entry.
    Content is already readable — combine heading + content.
    """
    heading = entry.get('heading', '')
    content = entry.get('content', '')

    if heading and content:
        return f"{heading}\n\n{content}"
    return content or heading


def chunk_structured_entry(entry: dict) -> str:
    """
    Process a 'structured' format entry.
    Apply the template to each item, then combine with heading.
    """
    heading = entry.get('heading', '')
    template = entry.get('template', '')
    items = entry.get('items', [])

    if not template or not items:
        print(f"  Warning: structured entry '{entry.get('id')}' missing template or items")
        return heading

    parts = [heading] if heading else []

    for item in items:
        try:
            text = template.format(**item)
            parts.append(text)
        except KeyError as e:
            print(f"  Warning: template placeholder {e} not found in item for entry '{entry.get('id')}'")
            continue

    return '\n'.join(parts)


def chunk_entry(entry: dict) -> str:
    """Route an entry to the correct chunker based on its format."""
    fmt = entry.get('format', 'text')

    if fmt in ('text', 'string'):
        text = chunk_text_entry(entry)
    elif fmt in ('structured', 'object'):
        text = chunk_structured_entry(entry)
    else:
        print(f"  Warning: unknown format '{fmt}' for entry '{entry.get('id')}', treating as text")
        text = chunk_text_entry(entry)

    search_terms = entry.get('search_terms', '')
    if search_terms:
        text = f"Search terms: {search_terms}\n\n{text}"

    return text


def load_bot_data(bot_id: str) -> list[dict]:
    """
    Main entry point. Load and chunk all data for a bot.

    Returns a list of dicts ready for embedding:
        {id, bot_id, category, heading, text}
    """
    print(f"Loading data for bot: {bot_id}")
    print(f"  Source: s3://{S3_BUCKET}/{S3_PREFIX}/{bot_id}/data/")

    entries = load_yaml_files(bot_id)

    if not entries:
        print(f"  No entries found for bot '{bot_id}'")
        return []

    chunks = []
    for entry in entries:
        text = chunk_entry(entry)

        if not text or not text.strip():
            print(f"  Skipping empty entry: {entry.get('id')}")
            continue

        chunks.append({
            'id': entry['id'],
            'bot_id': bot_id,
            'category': entry.get('category', 'General'),
            'heading': entry.get('heading', ''),
            'text': text
        })

    print(f"  Produced {len(chunks)} chunks for bot '{bot_id}'")
    return chunks
