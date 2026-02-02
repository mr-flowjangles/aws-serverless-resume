"""
RobbAI API Router
FastAPI endpoints for the chatbot functionality.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os

router = APIRouter(prefix="/ai", tags=["AI Chatbot"])


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    session_id: Optional[str] = None  # For future session management


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    sources: list[dict] = []


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    chatbot_enabled: bool
    embeddings_ready: bool


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if the AI chatbot is ready"""
    from ai.retrieval import get_dynamodb_connection
    
    chatbot_enabled = bool(os.getenv('OPENAI_API_KEY')) and bool(os.getenv('ANTHROPIC_API_KEY'))
    embeddings_ready = False
    
    if chatbot_enabled:
        try:
            dynamodb = get_dynamodb_connection()
            table = dynamodb.Table('ChatbotRAG')
            response = table.scan(Limit=1)
            embeddings_ready = bool(response.get('Items'))
        except Exception:
            embeddings_ready = False
    
    return HealthResponse(
        status="ok" if (chatbot_enabled and embeddings_ready) else "degraded",
        chatbot_enabled=chatbot_enabled,
        embeddings_ready=embeddings_ready
    )


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