#!/usr/bin/env python3
"""
RobbAI Chatbot Module
Uses RAG (Retrieval Augmented Generation) to answer questions about Rob.
"""
import os
from datetime import datetime
from pathlib import Path
import anthropic
from ai.retrieval import retrieve_relevant_chunks, format_context_for_llm

# Initialize Anthropic client
anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Load system prompt from file
PROMPT_FILE = Path(__file__).parent / 'prompts' / 'robbai_system.md'
with open(PROMPT_FILE, 'r') as f:
    SYSTEM_PROMPT_TEMPLATE = f.read()

# Inject current date into the prompt
current_date = datetime.now().strftime('%B %d, %Y')
SYSTEM_PROMPT = SYSTEM_PROMPT_TEMPLATE.format(current_date=current_date)

def generate_response(
    user_message: str,
    conversation_history: list[dict] = None,
    top_k: int = 5,
    similarity_threshold: float = 0.5
) -> dict:
    """
    Generate a response to the user's message using RAG.
    
    Args:
        user_message: The user's question or message
        conversation_history: Previous messages in the conversation
        top_k: Number of chunks to retrieve
        similarity_threshold: Minimum similarity for retrieval
    
    Returns:
        dict with 'response' text and 'sources' (retrieved chunks)
    """
    if conversation_history is None:
        conversation_history = []
    
    # Retrieve relevant context
    relevant_chunks = retrieve_relevant_chunks(
        query=user_message,
        top_k=top_k,
        similarity_threshold=similarity_threshold
    )
    
    # Format context for the prompt
    context = format_context_for_llm(relevant_chunks)
    
    # Build the messages array
    messages = []
    
    # Add conversation history (if any)
    for msg in conversation_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Add the current user message with context
    user_content = f"""## Relevant Context About Rob:
{context}

## User Question:
{user_message}

Remember: Keep your response short and conversational. Write in PLAIN TEXT ONLY - do not use ** or any markdown. If you can't answer from the context, say so politely."""

    messages.append({
        "role": "user",
        "content": user_content
    })
    
    # Call Claude API
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=messages
    )
    
    return {
        "response": response.content[0].text,
        "sources": [
            {
                "type": chunk["type"],
                "similarity": chunk["similarity"]
            }
            for chunk in relevant_chunks
        ]
    }


def chat(user_message: str, session_history: list[dict] = None) -> str:
    """
    Simple chat interface - returns just the response text.
    
    Args:
        user_message: What the user said
        session_history: Previous messages (optional)
    
    Returns:
        RobbAI's response as a string
    """
    result = generate_response(user_message, session_history)
    return result["response"]