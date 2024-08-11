from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from ..services.ai_service import AIService
from ..models.chat import ChatRequest

router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest):
    ai_service = AIService()
    conversation_service = ConversationService()

    async def event_stream():
        async for chunk in ai_service.get_ai_response(request.message, request.customer_info):
            yield f"data: {chunk}\n\n"
        
        # Uložení konverzace
        conversation_service.save_conversation(request.customer_info, request.message, "AI response")

    return StreamingResponse(event_stream(), media_type="text/event-stream")