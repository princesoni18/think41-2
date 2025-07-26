from fastapi import APIRouter
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.controllers.chat_controller import get_gemini_response

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_with_bot(request: ChatRequest):
    response_text = get_gemini_response(request.message)
    return ChatResponse(response=response_text)
