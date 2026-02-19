"""
If you do not want to use Bedrock, rename this file to chatbot.py and implement 
the same interface using the Anthropic API.
"""

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
from datetime import datetime
from pathlib import Path
import yaml
import anthropic
from .retrieval import retrieve_relevant_chunks, format_context_for_llm

# ---------------------------------------------------------------------------
# Cached resources — persist across warm Lambda invocations
# ---------------------------------------------------------------------------
_anthropic_client = None
_system_prompts = {}


def get_anthropic_client() -> anthropic.Anthropic:
    """Lazy-init Anthropic client."""
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    return _anthropic_client


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
    conversation_history: list[dict] = None,
    top_k: int = 5,
    similarity_threshold: float = 0.3
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
            "content": msg["content"]
        })

    # Add current user message with context
    user_content = f"""## Relevant Context:
{context}

## User Question:
{user_message}

Remember: Keep your response short and conversational. Write in PLAIN TEXT ONLY - do not use ** or any markdown. If you can't answer from the context, say so politely."""

    messages.append({
        "role": "user",
        "content": user_content
    })

    # Load this bot's system prompt
    system_prompt = load_system_prompt(bot_id)

    # Call Claude
    client = get_anthropic_client()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=system_prompt,
        messages=messages
    )

    return {
        "response": response.content[0].text,
        "sources": [
            {
                "category": chunk["category"],
                "similarity": chunk["similarity"]
            }
            for chunk in relevant_chunks
        ]
    }
