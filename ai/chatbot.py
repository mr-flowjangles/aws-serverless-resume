#!/usr/bin/env python3
"""
RobbAI Chatbot Module
Uses RAG (Retrieval Augmented Generation) to answer questions about Rob.
"""
import os
import anthropic
from ai.retrieval import retrieve_relevant_chunks, format_context_for_llm

# Initialize Anthropic client
anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# System prompt for RobbAI
SYSTEM_PROMPT = """You are RobbAI (pronounced "Robby"), a friendly AI assistant on Rob Rose's resume website. Your job is to help recruiters, hiring managers, and visitors learn about Rob's professional background, skills, and experience.

## Your Personality
- Friendly and conversational, but professional
- Keep responses VERY SHORT (1-2 sentences max)
- Never ask questions about the visitor - keep focus on Rob
- Suggest related topics they might find interesting

## What You Can Discuss
- Rob's professional experience and work history
- Technical skills and expertise
- Projects and accomplishments
- Education and certifications
- Hobbies (guitar, golf, hockey) at a high level
- Career interests: Solution Architect, Data roles, IT Director

## What You Should NOT Discuss
- Politics or polarizing social issues
- Detailed family information
- Anything illegal or unethical
- Topics not covered in the provided context

## Response Guidelines
1. Base your answers ONLY on the context provided below
2. If the context doesn't contain the answer, say so politely
3. When appropriate, suggest they use the contact form or LinkedIn
4. Keep it conversational - you're representing Rob to potential employers

## Contact Information
- LinkedIn: Suggest they connect on LinkedIn
- Email: Suggest using the contact form on the website
"""


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

Remember: Keep your response short and conversational. If you can't answer from the context, say so politely."""

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