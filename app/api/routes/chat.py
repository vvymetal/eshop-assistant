from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import StreamingResponse
from backend.app.services.ai_service import AIService, ConversationManager
from pydantic import BaseModel
import logging
import json
import asyncio
from backend.app.services.ai_service import AIService, ChatEventHandler
from backend.app.core.event_handler import ChatEventHandler
from backend.app.services.ai_service import AIService
from backend.app.services.tool_call_handler import ToolCallHandler
from backend.app.services.product_service import ProductService
from backend.app.services.cart_service import CartService

router = APIRouter()
ai_service = AIService()
product_service = ProductService()
cart_service = CartService()
tool_call_handler = ToolCallHandler(product_service, cart_service)


class MessageCreate(BaseModel):
    message: str

ai_service = AIService()
conversation_manager = ConversationManager(ai_service)

@router.post("/start")
async def start_chat():
    thread_id = conversation_manager.start_conversation()
    return {"thread_id": thread_id}

@router.post("/{thread_id}/send")
async def send_message(thread_id: str, message: MessageCreate):
    if not conversation_manager.get_conversation(thread_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    conversation_manager.add_message(thread_id, "user", message.message)
    return {"status": "Message sent"}

@router.get("/stream")
async def stream_message(request: Request):
    logging.info("Received stream request")
    try:
        message = request.query_params.get('message')
        context_str = request.query_params.get('context', '[]')
        thread_id = request.query_params.get('thread_id')
        instructions = request.query_params.get('instructions')

        if not message or not thread_id:
            raise HTTPException(status_code=400, detail="Message and thread_id are required")

        context = json.loads(context_str)

        logging.info(f'Streaming message: {message}')
        logging.info(f'Context: {context}')
        logging.info(f'Thread ID: {thread_id}')
        logging.info(f'Instructions: {instructions}')

        conversation = conversation_manager.get_conversation(thread_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        for msg in context:
            conversation_manager.add_message(thread_id, msg['role'], msg['content'])

        conversation_manager.add_message(thread_id, "user", message)

        async def event_generator():
            queue = asyncio.Queue()
            
            async def send_func(data):
                await queue.put(data)

            event_handler = ChatEventHandler(send_func)

            # Vytvoříme stream bez použití kontextového manažeru
            stream = ai_service.client.beta.threads.runs.stream(
                thread_id=thread_id,
                assistant_id=ai_service.assistant_id,
                instructions=instructions,
                event_handler=event_handler,
            )

            # Spustíme stream a počkáme na jeho dokončení
            await stream.until_done()

            while True:
                chunk = await queue.get()
                if chunk['type'] == 'end':
                    break
                yield f"data: {json.dumps(chunk)}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    

    except json.JSONDecodeError:
        logging.error("Invalid JSON in context parameter")
        raise HTTPException(status_code=400, detail="Invalid context format")
    except Exception as e:
        logging.error(f"Error in stream_message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    
    
