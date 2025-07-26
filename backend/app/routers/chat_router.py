

from fastapi import APIRouter
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.controllers.chat_controller import get_gemini_response
from app.controllers.conversation_controller import save_message_to_conversation
import uuid

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_with_bot(request: ChatRequest):
    # Generate a conversation_id if not provided
    conversation_id = request.conversation_id or str(uuid.uuid4())

    # Save user message
    save_message_to_conversation(
        user_id=request.user_id,
        conversation_id=conversation_id,
        sender="user",
        text=request.message
    )
    response_text = get_gemini_response(request.message)
    # Save bot response
    save_message_to_conversation(
        user_id=request.user_id,
        conversation_id=conversation_id,
        sender="bot",
        text=response_text
    )
    return ChatResponse(response=response_text)
