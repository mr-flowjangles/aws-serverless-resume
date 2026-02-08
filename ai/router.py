"""
RobbAI API Router
FastAPI endpoints for the chatbot functionality.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import os
import uuid
import yaml
from datetime import datetime

router = APIRouter(prefix="/ai", tags=["AI Chatbot"])


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    session_id: Optional[str] = None  # For future session management


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    sources: list[dict] = []


class ChatbotConfigResponse(BaseModel):
    """Response model for chatbot configuration"""
    enabled: bool
    name: str
    pronunciation: str
    personality: str


def log_chat_interaction(question: str, response: str, sources: list[dict]):
    """Log chat interaction to DynamoDB"""
    try:
        from ai.retrieval import get_dynamodb_connection
        from decimal import Decimal
        
        dynamodb = get_dynamodb_connection()
        table = dynamodb.Table('ChatbotLogs')
        
        # Convert float similarities to Decimal for DynamoDB
        clean_sources = [
            {
                'type': s['type'],
                'similarity': Decimal(str(s['similarity']))
            }
            for s in sources
        ]
        
        table.put_item(Item={
            'id': f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
            'timestamp': datetime.utcnow().isoformat(),
            'question': question,
            'response': response,
            'sources': clean_sources,
            'source_count': len(sources)
        })
    except Exception as e:
        print(f"Failed to log chat interaction: {e}")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to RobbAI and get a response.
    
    The chatbot uses RAG (Retrieval Augmented Generation) to find
    relevant information about Rob and generate helpful responses.
    """
    # Check if API keys are configured
    if not os.getenv('OPENAI_API_KEY'):
        raise HTTPException(
            status_code=503,
            detail="Chatbot not configured: missing OpenAI API key"
        )
    
    if not os.getenv('ANTHROPIC_API_KEY'):
        raise HTTPException(
            status_code=503,
            detail="Chatbot not configured: missing Anthropic API key"
        )
    
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )
    
    try:
        from ai.chatbot import generate_response
        
        result = generate_response(
            user_message=request.message,
            conversation_history=None,  # Stateless for now
            top_k=5,
            similarity_threshold=0.2
        )
        
        # Log the interaction
        log_chat_interaction(
            question=request.message,
            response=result["response"],
            sources=result["sources"]
        )
        
        return ChatResponse(
            response=result["response"],
            sources=result["sources"]
        )
        
    except Exception as e:
        # Log the error (you should use proper logging)
        print(f"Chatbot error: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your message"
        )


@router.get("/suggestions")
async def get_suggestions():
    """Return suggested questions visitors might want to ask"""
    return {
        "suggestions": [
            "What is Rob's current role?",
            "What are Rob's technical skills?",
            "Tell me about Rob's AWS experience",
            "What kind of roles is Rob interested in?",
            "Does Rob have any hobbies?"
        ]
    }


@router.get("/chatbot/config", response_model=ChatbotConfigResponse)
async def get_chatbot_config():
    """
    Return chatbot configuration from ai/config.yml
    Used by frontend to determine if chatbot widget should be displayed
    """
    try:
        # Path to config file (relative to this router file)
        config_path = Path(__file__).parent / 'config.yml'
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        chatbot_config = config.get('chatbot', {})
        
        return ChatbotConfigResponse(
            enabled=chatbot_config.get('enabled', False),
            name=chatbot_config.get('name', 'RobbAI'),
            pronunciation=chatbot_config.get('pronunciation', 'Robby'),
            personality=chatbot_config.get('personality', 'friendly')
        )
    except Exception as e:
        # If config file doesn't exist or error reading it, return disabled
        print(f"Error reading chatbot config: {e}")
        return ChatbotConfigResponse(
            enabled=False,
            name='RobbAI',
            pronunciation='Robby',
            personality='friendly'
        )