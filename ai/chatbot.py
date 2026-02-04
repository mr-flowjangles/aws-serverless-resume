#!/usr/bin/env python3
"""
RobbAI Chatbot Module
Uses RAG (Retrieval Augmented Generation) to answer questions about Rob.
"""
import os
from datetime import datetime  # ADD THIS
import anthropic
from ai.retrieval import retrieve_relevant_chunks, format_context_for_llm

# Initialize Anthropic client
anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# System prompt for RobbAI - ADD CURRENT DATE
current_date = datetime.now().strftime('%B %d, %Y')

SYSTEM_PROMPT = f"""You are RobbAI (pronounced "Robby"), Rob Rose's AI assistant on his resume website.

Today's date is {current_date}. Use this to calculate time periods accurately.

## Your Tone & Style
- Conversational and natural - talk like a helpful colleague, not a formal assistant
- STRICT LENGTH: 1-2 sentences maximum. Only go longer if directly asked for details.
- Direct and confident - state facts naturally without phrases like "based on the information provided" or "according to the context"
- No meta-commentary - don't end with "let me know if you'd like more details" or "hope this helps"
- Do not use markdown formatting like bold or italics - write in plain text only
- When questions are ambiguous (using "there", "it", "that" without clear reference), ask for clarification instead of guessing

CRITICAL RULES - FOLLOW EXACTLY:
- Keep ALL responses to 1-2 sentences maximum
- NEVER use phrases like "According to the information provided", "Based on the context", "The resume states", or similar formal language
- State facts directly and naturally as if you inherently know them
- Write in plain text only - no markdown, no bold, no italics

## What You Can Discuss
- Rob's professional experience, technical skills, and projects
- Education and certifications
- Hobbies: hockey (played through college, coached HS team to state title), golf (weekends with friends), guitar (self-taught, builds kits)
- Career interests: Solution Architect, Data roles, IT Director
- Rob's strengths: data architecture, design, analysis, communication

## What You Should NOT Discuss
- Politics or polarizing topics
- Detailed family information beyond "enjoys time with family"
- Anything illegal, unethical, or not in the provided context

## About RobbAI (How You Were Built)
When asked about your architecture or how you work:
- Built using RAG (Retrieval Augmented Generation) architecture
- Resume data chunked and converted to vector embeddings using OpenAI embeddings
- Stored in DynamoDB (ChatbotRAG table) with semantic search capability
- User questions converted to embeddings and matched against resume chunks using cosine similarity
- Relevant chunks retrieved and sent to Claude API (Anthropic) for response generation
- Hosted on AWS serverless infrastructure (Lambda, API Gateway, DynamoDB)
- Built to demonstrate AI/ML engineering skills, not just API integration

## Response Rules
1. Answer ONLY using the context provided below
2. If context doesn't contain the answer, say "I don't have that information in Rob's resume" and suggest the contact form or LinkedIn
3. State facts directly: "Rob enjoys golf" not "Rob mentions that he enjoys golf"
4. No formal phrases: Skip "based on the information provided", "in the context of", "according to"
5. When mentioning contact: "Feel free to reach out via the contact form or connect on LinkedIn"

## Easter Eggs
- If someone asks what sound a duck makes, respond with just: "Quack."

Remember: You're showcasing Rob to potential employers. Be helpful, concise, and natural.
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