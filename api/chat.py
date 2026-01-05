from fastapi import APIRouter
from models import ChatRequest, ChatResponse

router = APIRouter()

ABOUT_ME = "My name is Rob. I build cloud + backend systems."

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    return ChatResponse(answer=f"Q: {req.question} | A (stub): {ABOUT_ME}")
