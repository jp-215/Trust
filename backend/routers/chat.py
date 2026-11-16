"""Route: /chat"""

from fastapi import APIRouter

from handlers import chat_handler
from models.chat import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat interface — answers grounded in gold-table data via the Gemini agent."""
    return await chat_handler.chat(request)
