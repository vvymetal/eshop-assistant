import openai
from app.core.config import settings

class AIService:  # Ensure the class name matches the import statement
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.assistant_id = settings.ASSISTANT_ID
        self.thread = None

    async def create_thread(self):
        try:
            self.thread = await openai.beta.threads.create()
            return self.thread.id
        except Exception as e:
            print(f"Error creating thread: {e}")
            return None

    async def send_message(self, message: str):
        if not self.thread:
            thread_id = await self.create_thread()
            if not thread_id:
                return None

        try:
            await openai.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=message
            )

            run = await openai.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant_id
            )

            return run.id
        except Exception as e:
            print(f"Error sending message: {e}")
            return None

    async def get_response(self, run_id: str):
        try:
            run = await openai.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run_id
            )

            if run.status == 'completed':
                messages = await openai.beta.threads.messages.list(thread_id=self.thread.id)
                assistant_message = next((msg for msg in messages if msg.role == 'assistant'), None)
                if assistant_message:
                    return assistant_message.content[0].text.value

            return None
        except Exception as e:
            print(f"Error getting response: {e}")
            return None

    def create_assistant(self, name: str, description: str):
        # Implementation for creating an assistant
        pass