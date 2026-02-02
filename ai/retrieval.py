#!/usr/bin/env python3
"""
Retrieval Module for RobbAI
Performs semantic search against stored embeddings in DynamoDB.
"""
import os
import boto3
import numpy as np
from openai import OpenAI
from decimal import Decimal

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def get_dynamodb_connection():
    """Get DynamoDB connection (works with LocalStack or AWS)"""
    endpoint_url = os.getenv('AWS_ENDPOINT_URL', 'http://localhost:4566')
    
    if endpoint_url == "":
        # Real AWS
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    else:
        # LocalStack
        dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=endpoint_url,
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'test'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'test')
        )
    return dynamodb


def generate_query_embedding(query: str) -> list[float]:
    """Convert user query to embedding vector"""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    return response.data[0].embedding


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    a = np.array(vec1)
    b = np.array(vec2)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def retrieve_relevant_chunks(
    query: str,
    top_k: int = 5,
    similarity_threshold: float = 0.7
) -> list[dict]:
    """
    Retrieve the most relevant chunks for a given query.
    
    Args:
        query: User's question
        top_k: Number of top results to return
        similarity_threshold: Minimum similarity score (0-1)
    
    Returns:
        List of relevant chunks with similarity scores
    """
    # Generate embedding for the query
    query_embedding = generate_query_embedding(query)
    
    # Get all embeddings from DynamoDB
    dynamodb = get_dynamodb_connection()
    table = dynamodb.Table('ChatbotRAG')
    
    response = table.scan()
    items = response.get('Items', [])
    
    # Handle pagination
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
    
    # Calculate similarity for each chunk
    results = []
    for item in items:
        # Convert Decimal embedding back to floats
        stored_embedding = [float(x) for x in item['embedding']]
        
        similarity = cosine_similarity(query_embedding, stored_embedding)
        
        if similarity >= similarity_threshold:
            results.append({
                'id': item['id'],
                'type': item['type'],
                'text': item['text'],
                'source': item.get('source', 'resume'),
                'similarity': float(similarity),
                # Include metadata if present
                'company': item.get('company'),
                'job_title': item.get('job_title'),
                'category': item.get('category')
            })
    
    # Sort by similarity (highest first) and return top K
    results.sort(key=lambda x: x['similarity'], reverse=True)
    return results[:top_k]


def format_context_for_llm(chunks: list[dict]) -> str:
    """
    Format retrieved chunks into context for the LLM.
    
    Args:
        chunks: List of retrieved chunks with similarity scores
    
    Returns:
        Formatted string to include in LLM prompt
    """
    if not chunks:
        return "No relevant information found."
    
    context_parts = []
    for chunk in chunks:
        context_parts.append(f"[{chunk['type'].upper()}]\n{chunk['text']}")
    
    return "\n\n---\n\n".join(context_parts)