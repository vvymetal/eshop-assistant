from openai import AsyncOpenAI
from backend.app.core.config import settings
import asyncio


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.assistant_id = settings.ASSISTANT_ID
        self.thread = None

    async def create_thread(self):
        try:
            self.thread = await self.client.beta.threads.create()
            return self.thread.id
        except Exception as e:
            print(f"Error creating thread: {e}")
            return None

    async def add_message_to_thread(self, message: str, role: str = "user"):
        if not self.thread:
            await self.create_thread()
        
        await self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role=role,
            content=message
        )

    async def run_assistant(self):
        try:
            run = await self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant_id,
                stream=True
            )
            
            async for event in run:
                if event.event == "message_created":
                    message = await self.client.beta.threads.messages.retrieve(
                        thread_id=self.thread.id,
                        message_id=event.data.id
                    )
                    for content in message.content:
                        if content.type == 'text':
                            yield content.text.value
                elif event.event == "run_completed":
                    return
                elif event.event in ["run_failed", "run_cancelled"]:
                    raise Exception(f"Run ended with status: {event.event}")

        except Exception as e:
            print(f"Error in run_assistant: {e}")
            yield f"An error occurred: {str(e)}"

    async def create_assistant(self, name: str, description: str):
        # Implementation for creating an assistant
        # Note: This is a placeholder. You'll need to implement the actual logic
        # to create an assistant using the OpenAI API if it doesn't already exist.
        pass

    async def send_message(self, message: str):
        if not self.thread:
            thread_id = await self.create_thread()
            if not thread_id:
                return None

        try:
            await self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=message
            )

            run = await self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant_id
            )

            return run.id
        except Exception as e:
            print(f"Error sending message: {e}")
            return None

    async def get_response(self, run_id: str):
        try:
            run = await self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run_id
            )

            if run.status == 'completed':
                messages = await self.client.beta.threads.messages.list(thread_id=self.thread.id)
                for message in messages.data:
                    if message.role == 'assistant':
                        for content in message.content:
                            if content.type == 'text':
                                return content.text.value
            elif run.status in ['failed', 'cancelled']:
                return None
            return None  # Return None if the run is still in progress
        except Exception as e:
            print(f"Error getting response: {e}")
            return None