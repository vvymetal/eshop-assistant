from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.app.core.config import settings
import logging
import json
import asyncio
from openai import OpenAI
from openai.types.beta.threads import Run
from typing_extensions import override

router = APIRouter()

class AIService:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        self.client = OpenAI(api_key=api_key or settings.OPENAI_API_KEY)
        self.model = model
        self.assistant = self.create_assistant()

    def create_assistant(self):
        return self.client.beta.assistants.create(
            name="eShop Assistant",
            instructions="You are an AI assistant for an e-commerce platform. Help users find products, manage their cart, and answer questions about the shopping process.",
            tools=self.default_tools(),
            model=self.model
        )

    def default_tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_product_info",
                    "description": "Get information about a specific product",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "string", "description": "The ID of the product"}
                        },
                        "required": ["product_id"]
                    }
                }
            },
            # Add other tools here...
        ]

    def create_thread(self):
        return self.client.beta.threads.create()

    def add_message_to_thread(self, thread_id: str, role: str, content: str):
        return self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content
        )

    def run_assistant(self, thread_id: str, instructions: str = None):
        return self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant.id,
            instructions=instructions
        )

    def get_run_status(self, thread_id: str, run_id: str) -> Run:
        return self.client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )

    def get_messages(self, thread_id: str):
        return self.client.beta.threads.messages.list(thread_id=thread_id)

class EventHandler:
    def __init__(self, handle_chunk_func):
        self.handle_chunk_func = handle_chunk_func

    @override
    def on_text_created(self, text) -> None:
        self.handle_chunk_func({"type": "start", "content": ""})

    @override
    def on_text_delta(self, delta, snapshot):
        self.handle_chunk_func({"type": "stream", "content": delta.value})

    def on_tool_call_created(self, tool_call):
        self.handle_chunk_func({"type": "tool_call", "content": str(tool_call)})

    def on_tool_call_delta(self, delta, snapshot):
        self.handle_chunk_func({"type": "tool_call_delta", "content": str(delta)})

    @classmethod
    def on_end(cls):
        print("\n\nAll streams have ended.")

ai_service = AIService()

@router.post("/start")
async def start_chat():
    thread = ai_service.create_thread()
    return {"thread_id": thread.id}

@router.get("/stream")
async def stream_message(request: Request):
    logging.info("Received stream request")
    try:
        message = request.query_params.get('message')
        thread_id = request.query_params.get('thread_id')
        instructions = request.query_params.get('instructions')

        if not message or not thread_id:
            raise HTTPException(status_code=400, detail="Message and thread_id are required")

        logging.info(f'Streaming message: {message}')
        logging.info(f'Thread ID: {thread_id}')
        logging.info(f'Instructions: {instructions}')

        ai_service.add_message_to_thread(thread_id, "user", message)

        async def event_generator():
            run = ai_service.run_assistant(thread_id, instructions)
            
            while True:
                run_status = ai_service.get_run_status(thread_id, run.id)
                if run_status.status == "completed":
                    messages = ai_service.get_messages(thread_id)
                    for message in messages.data:
                        if message.role == "assistant":
                            yield f"data: {json.dumps({'type': 'stream', 'content': message.content[0].text.value})}\n\n"
                    break
                elif run_status.status == "failed":
                    yield f"data: {json.dumps({'type': 'error', 'content': 'Run failed'})}\n\n"
                    break
                await asyncio.sleep(1)  # Poll every second

            yield f"data: {json.dumps({'type': 'end', 'content': ''})}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        logging.error(f"Error in stream_message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))