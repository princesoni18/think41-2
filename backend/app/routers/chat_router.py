
from fastapi import APIRouter
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.controllers.chat_controller import get_gemini_response
from app.controllers.conversation_controller import save_message_to_conversation

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat_with_bot(request: ChatRequest):
    # Save user message
    if request.conversation_id:
        save_message_to_conversation(
            user_id=request.user_id,  # Replace with actual user_id if available
            conversation_id=request.conversation_id,
            sender="user",
            text=request.message
        )
    response_text = get_gemini_response(request.message)
    # Save bot response
    if request.conversation_id:
        save_message_to_conversation(
            user_id=request.user_id,  # Replace with actual user_id if available
            conversation_id=request.conversation_id,
            sender="bot",
            text=response_text
        )
    return ChatResponse(response=response_text)
