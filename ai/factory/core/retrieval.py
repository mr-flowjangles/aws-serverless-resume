"""
Retrieval Module (Parameterized)

Performs semantic search against stored embeddings in DynamoDB,
scoped by bot_id. Each bot's embeddings are cached separately
in memory for warm Lambda reuse.

Same math as ai/retrieval.py — cosine similarity, top-K, threshold.
Only difference: everything is filtered by bot_id.
"""
import os
import json
import time
import logging
import boto3
import numpy as np

logger = logging.getLogger(__name__)

BEDROCK_MODEL_ID = "amazon.titan-embed-text-v2:0"
EMBEDDING_DIMENSIONS = 1024

# ---------------------------------------------------------------------------
# Per-bot embedding cache — keyed by bot_id
# Survives across warm Lambda invocations
# ---------------------------------------------------------------------------
_embeddings_cache = {}


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


def get_cached_embeddings(bot_id: str) -> list[dict]:
    """
    Load and cache embeddings for a specific bot.
    Only returns rows where bot_id matches.
    """
    global _embeddings_cache

    if bot_id in _embeddings_cache:
        logger.info(f"[retrieval:{bot_id}] cache HIT — {len(_embeddings_cache[bot_id])} items")
        return _embeddings_cache[bot_id]

    logger.info(f"[retrieval:{bot_id}] cache MISS — scanning DynamoDB...")
    t_start = time.time()

    dynamodb = get_dynamodb_connection()
    table = dynamodb.Table('ChatbotRAG')

    response = table.scan()
    items = response.get('Items', [])
    pages = 1

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
        pages += 1

    t_scan = time.time() - t_start
    logger.info(f"[retrieval:{bot_id}] DynamoDB scan complete — {len(items)} total items, {pages} page(s), {t_scan:.3f}s")

    # Filter to this bot only
    bot_items = [item for item in items if item.get('bot_id') == bot_id]

    _embeddings_cache[bot_id] = bot_items
    logger.info(f"[retrieval:{bot_id}] cached {len(bot_items)} embeddings (filtered from {len(items)} total)")
    return bot_items


# ---------------------------------------------------------------------------
# Bedrock query embedding
# ---------------------------------------------------------------------------

_bedrock_client = None


def get_bedrock_client():
    """Lazy-init Bedrock runtime client."""
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
    return _bedrock_client


def generate_query_embedding(query: str) -> list[float]:
    """Convert a user's question to an embedding vector via Bedrock Titan V2."""
    t_start = time.time()
    client = get_bedrock_client()
    response = client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps({
            "inputText": query,
            "dimensions": EMBEDDING_DIMENSIONS,
            "normalize": True
        })
    )
    embedding = json.loads(response['body'].read())['embedding']
    logger.info(f"[retrieval] Bedrock embedding={time.time() - t_start:.3f}s")
    return embedding


# ---------------------------------------------------------------------------
# Similarity search
# ---------------------------------------------------------------------------

def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    a = np.array(vec1)
    b = np.array(vec2)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def retrieve_relevant_chunks(
    bot_id: str,
    query: str,
    top_k: int,
    similarity_threshold: float
) -> list[dict]:
    """
    Retrieve the most relevant chunks for a user's query, scoped to a bot.
    """
    logger.info(f"[retrieval:{bot_id}] query='{query[:60]}'")

    # Convert question to embedding
    query_embedding = generate_query_embedding(query)

    # Get this bot's cached embeddings
    items = get_cached_embeddings(bot_id)

    # Log top scores for debugging
    all_scores = []
    for item in items:
        stored_embedding = [float(x) for x in item['embedding']]
        similarity = cosine_similarity(query_embedding, stored_embedding)
        all_scores.append((similarity, item.get('category', ''), item.get('heading', '')))
    all_scores.sort(reverse=True)
    for score, cat, heading in all_scores[:5]:
        logger.debug(f"[retrieval:{bot_id}] top_score={score:.4f} | {cat}: {heading}")

    # Calculate similarity for each chunk
    results = []
    for item in items:
        stored_embedding = [float(x) for x in item['embedding']]
        similarity = cosine_similarity(query_embedding, stored_embedding)

        if similarity >= similarity_threshold:
            results.append({
                'id': item['id'],
                'category': item.get('category', 'General'),
                'heading': item.get('heading', ''),
                'text': item['text'],
                'similarity': float(similarity),
            })

    results.sort(key=lambda x: x['similarity'], reverse=True)

    logger.info(
        f"[retrieval:{bot_id}] found={len(results)} above threshold={similarity_threshold} "
        f"top_score={results[0]['similarity']:.4f if results else 'N/A'} "
        f"returning top_{top_k}"
    )

    return results[:top_k]


def format_context_for_llm(chunks: list[dict]) -> str:
    """
    Format retrieved chunks into context string for Claude.
    """
    if not chunks:
        return "No relevant information found."

    context_parts = []
    for chunk in chunks:
        context_parts.append(f"[{chunk['category'].upper()}]\n{chunk['text']}")

    return "\n\n---\n\n".join(context_parts)
