"""
Router Factory

Creates a FastAPI APIRouter for any bot given a bot_id.
Each bot gets:
  - POST /{bot_id}/chat         Send a message, get a response
  - GET  /{bot_id}/config       Frontend config (enabled, name, etc.)
  - GET  /{bot_id}/suggestions  Suggested starter questions

Usage in main.py:
    from ai.factory.core.router import create_bot_router
    app.include_router(create_bot_router("guitar"), prefix=prefix)

Or let the factory auto-discover bots:
    from ai.factory import factory_router
    app.include_router(factory_router, prefix=prefix)
"""
import os
import uuid
import yaml
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional


# ---------------------------------------------------------------------------
# Request/Response models
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    """A single message in the conversation history."""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    session_id: Optional[str] = None
    conversation_history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    sources: list[dict] = []


class BotConfigResponse(BaseModel):
    """Response model for bot configuration."""
    enabled: bool
    name: str
    personality: str


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

def load_bot_config(bot_id: str) -> dict:
    """Load a bot's config.yml."""
    config_path = Path(__file__).parent.parent / 'bots' / bot_id / 'config.yml'

    if not config_path.exists():
        raise FileNotFoundError(f"No config.yml found for bot '{bot_id}'")

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Chat logging
# ---------------------------------------------------------------------------

def log_chat_interaction(bot_id: str, question: str, response: str, sources: list[dict]):
    """Log chat interaction to DynamoDB ChatbotLogs table."""
    try:
        from .retrieval import get_dynamodb_connection
        from decimal import Decimal

        dynamodb = get_dynamodb_connection()
        table = dynamodb.Table('ChatbotLogs')

        clean_sources = [
            {
                'category': s.get('category', 'unknown'),
                'similarity': Decimal(str(s.get('similarity', 0)))
            }
            for s in sources
        ]

        table.put_item(Item={
            'id': f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}",
            'bot_id': bot_id,
            'timestamp': datetime.utcnow().isoformat(),
            'question': question,
            'response': response,
            'sources': clean_sources,
            'source_count': len(sources)
        })
    except Exception as e:
        print(f"Failed to log chat interaction for '{bot_id}': {e}")


# ---------------------------------------------------------------------------
# Router factory
# ---------------------------------------------------------------------------

def create_bot_router(bot_id: str) -> APIRouter:
    """
    Create a FastAPI router for a specific bot.

    Args:
        bot_id: The bot folder name (e.g., 'guitar')

    Returns:
        APIRouter with /chat, /config, and /suggestions endpoints
    """
    router = APIRouter(prefix=f"/{bot_id}", tags=[f"{bot_id} chatbot"])

    @router.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        """Send a message to this bot and get a response."""
        if not os.getenv('OPENAI_API_KEY'):
            raise HTTPException(status_code=503, detail="Missing OpenAI API key")

        if not os.getenv('ANTHROPIC_API_KEY'):
            raise HTTPException(status_code=503, detail="Missing Anthropic API key")

        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        try:
            # Load config for RAG settings
            config = load_bot_config(bot_id)
            rag_config = config.get('bot', {}).get('rag', {})

            from .chatbot import generate_response

            result = generate_response(
                bot_id=bot_id,
                user_message=request.message,
                conversation_history=[msg.model_dump() for msg in request.conversation_history],
                top_k=rag_config.get('top_k', 5),
                similarity_threshold=rag_config.get('similarity_threshold')
            )

            # Log the interaction
            log_chat_interaction(
                bot_id=bot_id,
                question=request.message,
                response=result["response"],
                sources=result["sources"]
            )

            return ChatResponse(
                response=result["response"],
                sources=result["sources"]
            )

        except Exception as e:
            print(f"Chatbot error ({bot_id}): {e}")
            raise HTTPException(status_code=500, detail="Error processing your message")

    @router.get("/config", response_model=BotConfigResponse)
    async def get_config():
        """Return bot configuration for the frontend."""
        try:
            config = load_bot_config(bot_id)
            bot_config = config.get('bot', {})

            return BotConfigResponse(
                enabled=bot_config.get('enabled', False),
                name=bot_config.get('name', bot_id),
                personality=bot_config.get('personality', 'friendly')
            )
        except Exception as e:
            print(f"Config error ({bot_id}): {e}")
            return BotConfigResponse(
                enabled=False,
                name=bot_id,
                personality='friendly'
            )

    @router.get("/suggestions")
    async def get_suggestions():
        """Return suggested starter questions."""
        try:
            config = load_bot_config(bot_id)
            return {"suggestions": config.get('suggestions', [])}
        except Exception:
            return {"suggestions": []}

    @router.get("/warmup")
    async def warmup():
        """Preload embedding cache so first question is fast."""
        try:
            from .retrieval import get_cached_embeddings
            embeddings = get_cached_embeddings(bot_id)
            return {"status": "warm", "embeddings": len(embeddings)}
        except Exception as e:
            print(f"Warmup error ({bot_id}): {e}")
            return {"status": "error"}

    return router