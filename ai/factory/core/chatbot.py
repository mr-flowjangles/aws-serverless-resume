"""
Chatbot Module (Parameterized)

Generates responses using Claude API with RAG context.
Loads the system prompt from each bot's prompt.md file and
caches it per bot_id for warm Lambda reuse.

Same pattern as ai/chatbot.py — retrieve context, build messages,
call Claude. Only difference: bot_id drives which prompt and
embeddings are used.
"""
import os
import time
import logging
from datetime import datetime
from pathlib import Path
from pyexpat.errors import messages
import yaml
import boto3
import botocore.session
import configparser
from .retrieval import retrieve_relevant_chunks, format_context_for_llm

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cached resources — persist across warm Lambda invocations
# ---------------------------------------------------------------------------
_anthropic_client = None
_system_prompts = {}


_bedrock_client = None

def get_bedrock_client():
    global _bedrock_client
    if _bedrock_client is None:
        t_start = time.time()
        logger.info("[chatbot] Initializing Bedrock client...")
        try:
            config = configparser.ConfigParser()
            config.read('/root/.aws/credentials')
            _bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name='us-east-1',
                endpoint_url=os.getenv('BEDROCK_ENDPOINT_URL'),
                aws_access_key_id=config.get('default', 'aws_access_key_id'),
                aws_secret_access_key=config.get('default', 'aws_secret_access_key')
            )
            logger.info(f"[chatbot] Bedrock init via credentials file — {time.time() - t_start:.3f}s")
        except Exception:
            _bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name='us-east-1'
            )
            logger.info(f"[chatbot] Bedrock init via IAM role — {time.time() - t_start:.3f}s")
    return _bedrock_client

def load_system_prompt(bot_id: str) -> str:
    """
    Load and cache the system prompt for a bot.
    Reads from bots/{bot_id}/prompt.md and injects current date.
    """
    global _system_prompts

    if bot_id in _system_prompts:
        return _system_prompts[bot_id]

    prompt_path = Path(__file__).parent.parent / 'bots' / bot_id / 'prompt.yml'

    if not prompt_path.exists():
        raise FileNotFoundError(f"No prompt.yml found for bot '{bot_id}' at {prompt_path}")

    with open(prompt_path, 'r') as f:
        data = yaml.safe_load(f)

    template = data.get('prompt', '')

    # Inject current date
    current_date = datetime.now().strftime('%B %d, %Y')
    prompt = template.format(current_date=current_date)

    _system_prompts[bot_id] = prompt
    return prompt


def generate_response(
    bot_id: str,
    user_message: str,
    top_k: int,
    similarity_threshold: float,
    conversation_history: list[dict] = None,

) -> dict:
    """
    Generate a response using RAG for a specific bot.

    Args:
        bot_id: Which bot is responding
        user_message: The user's question
        conversation_history: Previous messages (optional)
        top_k: Number of chunks to retrieve
        similarity_threshold: Minimum similarity for retrieval

    Returns:
        dict with 'response' text and 'sources' list
    """
    if conversation_history is None:
        conversation_history = []

    # Retrieve relevant context for this bot
    relevant_chunks = retrieve_relevant_chunks(
        bot_id=bot_id,
        query=user_message,
        top_k=top_k,
        similarity_threshold=similarity_threshold
    )

    # Format context for the prompt
    context = format_context_for_llm(relevant_chunks)

    # Build messages array
    messages = []

    # Add conversation history
    for msg in conversation_history:
        messages.append({
            "role": msg["role"],
            "content": [{"text": msg["content"]}]
    })

    # Add current user message with context
    user_content = f"""## Relevant Context:
{context}

## User Question:
{user_message}

Remember: Keep your response short and conversational. Write in PLAIN TEXT ONLY - do not use ** or any markdown. If you can't answer from the context, say so politely."""

    messages.append({
        "role": "user",
        "content": [{"text": user_content}]
    })

    # Load this bot's system prompt
    system_prompt = load_system_prompt(bot_id)

    # Call Claude
    client = get_bedrock_client()
    response = client.converse(
        modelId="us.anthropic.claude-sonnet-4-20250514-v1:0",
        inferenceConfig={"maxTokens": 1000},
        system=[{"text": system_prompt}],
        messages=messages)

    return {
        "response": response["output"]["message"]["content"][0]["text"],
        "sources": [
            {
                "category": chunk["category"],
                "similarity": chunk["similarity"]
            }
            for chunk in relevant_chunks
        ]
    }

def generate_response_stream(
    bot_id: str,
    user_message: str,
    top_k: int,
    similarity_threshold: float,
    conversation_history: list[dict] = None,
):
    """
    Same as generate_response, but yields text chunks for streaming.
    """
    logger.info(f"[chatbot:{bot_id}] stream start query='{user_message[:60]}'")

    if conversation_history is None:
        conversation_history = []

    relevant_chunks = retrieve_relevant_chunks(
        bot_id=bot_id,
        query=user_message,
        top_k=top_k,
        similarity_threshold=similarity_threshold
    )

    context = format_context_for_llm(relevant_chunks)

    messages = []
    for msg in conversation_history:
        messages.append({
            "role": msg["role"],
            "content": [{"text": msg["content"]}]
        })

    user_content = f"""## Relevant Context:
{context}

## User Question:
{user_message}

Remember: Keep your response short and conversational. Write in PLAIN TEXT ONLY - do not use ** or any markdown. If you can't answer from the context, say so politely."""

    messages.append({
        "role": "user",
        "content": [{"text": user_content}]
    })

    system_prompt = load_system_prompt(bot_id)

    client = get_bedrock_client()
    response = client.converse_stream(
        modelId="us.anthropic.claude-sonnet-4-20250514-v1:0",
        inferenceConfig={"maxTokens": 1000},
        system=[{"text": system_prompt}],
        messages=messages
    )

    for event in response["stream"]:
        if "contentBlockDelta" in event:
            yield event["contentBlockDelta"]["delta"]["text"]