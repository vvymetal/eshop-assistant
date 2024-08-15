from openai import AsyncOpenAI, AsyncStream, AssistantEventHandler
from backend.app.core.config import settings
import asyncio
import json

class MyEventHandler(AssistantEventHandler):
    async def on_text_delta(self, delta, snapshot):
        yield f"data: {json.dumps({'content': delta.value})}\n\n"

    async def on_tool_call_created(self, tool_call):
        yield f"data: {json.dumps({'tool_call': str(tool_call)})}\n\n"

    async def on_tool_call_delta(self, delta, snapshot):
        yield f"data: {json.dumps({'tool_call_delta': str(delta)})}\n\n"

class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.assistant_id = settings.ASSISTANT_ID
        self.thread = None

    async def create_thread(self):
        self.thread = await self.client.beta.threads.create()
        return self.thread.id

    async def add_message_to_thread(self, message: str, role: str = "user"):
        if not self.thread:
            await self.create_thread()
        
        await self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role=role,
            content=message
        )

    async def run_assistant_stream(self):
        run = await self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant_id
        )

        async def event_generator():
            async with self.client.beta.threads.runs.stream(
                thread_id=self.thread.id,
                run_id=run.id,
                event_handler=MyEventHandler(),
            ) as stream:
                async for event in stream:
                    if isinstance(event, AsyncStream.TextDeltaEvent):
                        yield f"data: {json.dumps({'content': event.data.delta.value})}\n\n"
                    elif isinstance(event, AsyncStream.RunStepEvent):
                        yield f"data: {json.dumps({'status': event.data.status})}\n\n"
                yield "data: [DONE]\n\n"

        return event_generator()