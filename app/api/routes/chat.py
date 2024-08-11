from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from app.services.ai_service import AIService
from app.core.config import settings
import logging

router = APIRouter()
ai_service = AIService()

@router.on_event("startup")
async def startup_event():
    ai_service.create_assistant("E-shop Assistant", "You are an assistant helping customers with their purchases.")
    ai_service.create_thread()

@router.post("/chat")
async def send_message(request: Request):
    data = await request.json()
    message = data.get('message')
    ai_service.add_message_to_thread(message)
    response = ai_service.run_assistant()
    
    logging.info(f'Controller response: {response}')
    
    return {"response": response}

@router.post("/chat/stream")
async def stream_message(request: Request):
    data = await request.json()
    message = data.get('message')
    context = data.get('context', [])
    
    logging.info(f'Streaming message: {message}')
    logging.info(f'Context: {context}')

    async def event_generator():
        for msg in context:
            ai_service.add_message_to_thread(msg['content'], msg['role'])
        
        ai_service.add_message_to_thread(message)
        stream = ai_service.run_assistant()

        data_buffer = ''
        while True:
            chunk = await stream.read(8192)
            if not chunk:
                break
            data_buffer += chunk.decode('utf-8')

            while '\n\n' in data_buffer:
                line, data_buffer = data_buffer.split('\n\n', 1)
                if line.startswith('data: '):
                    data = line[6:].strip()
                    yield f"data: {data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")