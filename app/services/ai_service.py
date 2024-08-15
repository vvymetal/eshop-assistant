from openai import OpenAI
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.app.core.config import settings
import logging
from openai import AssistantEventHandler

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

    def run_assistant(self, thread_id: str, instructions: str = None, event_handler=None):
        with self.client.beta.threads.runs.create_and_stream(
            thread_id=thread_id,
            assistant_id=self.assistant.id,
            instructions=instructions,
            event_handler=event_handler,
        ) as stream:
            stream.until_done()
            return stream.get_final_run()

class EventHandler(AssistantEventHandler):
    def __init__(self, handle_chunk_func):
        self.handle_chunk_func = handle_chunk_func

    def on_text_created(self, text):
        self.handle_chunk_func({"type": "start", "content": ""})

    def on_text_delta(self, delta, snapshot):
        self.handle_chunk_func({"type": "stream", "content": delta.value})

    def on_tool_call_created(self, tool_call):
        self.handle_chunk_func({"type": "tool_call", "content": str(tool_call)})

    def on_tool_call_delta(self, delta, snapshot):
        self.handle_chunk_func({"type": "tool_call_delta", "content": str(delta)})

    def on_end(self):
        self.handle_chunk_func({"type": "end", "content": ""})