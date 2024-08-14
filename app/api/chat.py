from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from app.services.ai_service import AIService
import asyncio

router = APIRouter()
ai_service = AIService()

@router.on_event("startup")
async def startup_event():
    await ai_service.create_thread()

@router.get("/chat")
async def chat_endpoint(request: Request, message: str):
    async def event_generator():
        run_id = await ai_service.send_message(message)

        while True:
            if await request.is_disconnected():
                break

            response = await ai_service.get_response(run_id)
            if response:
                yield f"data: {response}\n\n"
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")