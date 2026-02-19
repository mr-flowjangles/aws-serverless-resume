"""
Retrieval Module (Parameterized)

Performs semantic search against stored embeddings in DynamoDB,
scoped by bot_id. Each bot's embeddings are cached separately
in memory for warm Lambda reuse.

Same math as ai/retrieval.py — cosine similarity, top-K, threshold.
Only difference: everything is filtered by bot_id.
"""
import os
import boto3
import numpy as np
from openai import OpenAI

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
        print(f"Using cached embeddings for '{bot_id}'")
        return _embeddings_cache[bot_id]

    print(f"Loading embeddings for '{bot_id}' from DynamoDB...")
    dynamodb = get_dynamodb_connection()
    table = dynamodb.Table('ChatbotRAG')

    response = table.scan()
    items = response.get('Items', [])

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))

    # Filter to this bot only
    bot_items = [item for item in items if item.get('bot_id') == bot_id]

    _embeddings_cache[bot_id] = bot_items
    print(f"Cached {len(bot_items)} embeddings for '{bot_id}'")
    return bot_items


# ---------------------------------------------------------------------------
# OpenAI query embedding
# ---------------------------------------------------------------------------

_openai_client = None


def get_openai_client() -> OpenAI:
    """Lazy-init OpenAI client."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    return _openai_client


def generate_query_embedding(query: str) -> list[float]:
    """Convert a user's question to an embedding vector."""
    print(f"[STREAM] Embedding query: {query[:50]}...")  # STREAM_DEBUG
    client = get_openai_client()
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    return response.data[0].embedding


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

    Args:
        bot_id: Which bot's embeddings to search
        query: The user's question
        top_k: Number of top results to return
        similarity_threshold: Minimum similarity score (0-1)

    Returns:
        List of relevant chunks with similarity scores
    """
    print(f"Retrieval for '{bot_id}': {query}")

    # Convert question to embedding
    query_embedding = generate_query_embedding(query)

    # Get this bot's cached embeddings
    items = get_cached_embeddings(bot_id)
    print(f"Searching {len(items)} embeddings...")


    all_scores = []
    for item in items:
        stored_embedding = [float(x) for x in item['embedding']]
        similarity = cosine_similarity(query_embedding, stored_embedding)
        all_scores.append((similarity, item.get('category', ''), item.get('heading', '')))
    all_scores.sort(reverse=True)
    for score, cat, heading in all_scores[:5]:
        print(f"  Score: {score:.4f} | {cat}: {heading}")


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
    print(f"[STREAM] Retrieved {len(results)} chunks, top score: {results[0]['similarity'] if results else 'N/A'}")  # STREAM_DEBUG
    print(f"Found {len(results)} results above threshold ({similarity_threshold})")

    print(f"  Above 0.6: {len([r for r in results if r['similarity'] >= 0.6])}")
    print(f"  Above 0.55: {len([r for r in results if r['similarity'] >= 0.55])}")
    print(f"  Above 0.5: {len([r for r in results if r['similarity'] >= 0.5])}")

    # Sort by similarity (highest first) and return top K
    results.sort(key=lambda x: x['similarity'], reverse=True)
    print(f"Found {len(results)} above threshold, returning top {top_k}")
    return results[:top_k]


def format_context_for_llm(chunks: list[dict]) -> str:
    """
    Format retrieved chunks into context string for Claude.

    Args:
        chunks: List of retrieved chunks with similarity scores

    Returns:
        Formatted string to include in the LLM prompt
    """
    if not chunks:
        return "No relevant information found."

    context_parts = []
    for chunk in chunks:
        context_parts.append(f"[{chunk['category'].upper()}]\n{chunk['text']}")

    return "\n\n---\n\n".join(context_parts)
