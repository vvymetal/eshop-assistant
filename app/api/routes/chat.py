from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from backend.app.services.ai_service import AIService
import logging
import asyncio
import json
from typing import AsyncGenerator

router = APIRouter()
ai_service = AIService()

@router.on_event("startup")
async def startup_event():
    await ai_service.create_assistant("E-shop Assistant", "You are an assistant helping customers with their purchases.")
    await ai_service.create_thread()

@router.get("/")
async def get_chat_status():
    return {"status": "Chat is ready"}

@router.post("/")
async def send_message(request: Request):
    data = await request.json()
    message = data.get('message')
    await ai_service.add_message_to_thread(message)
    response = await ai_service.run_assistant()
    logging.info(f'Controller response: {response}')
    return {"response": response}

@router.post("/stream")
async def stream_message(request: Request):
    data = await request.json()
    message = data.get('message')
    context = data.get('context', [])
    
    for msg in context:
        await ai_service.add_message_to_thread(msg['content'], msg['role'])
    
    await ai_service.add_message_to_thread(message)

    async def event_generator():
        async for response_chunk in ai_service.run_assistant():
            yield f"data: {json.dumps({'content': response_chunk})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")