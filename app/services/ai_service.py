import openai
from app.core.config import settings

class AiService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.assistant_id = settings.ASSISTANT_ID
        self.thread = None

    async def create_thread(self):
        self.thread = await openai.beta.threads.create()
        return self.thread.id

    async def send_message(self, message: str):
        if not self.thread:
            await self.create_thread()

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

    async def get_response(self, run_id: str):
        run = await openai.beta.threads.runs.retrieve(
            thread_id=self.thread.id,
            run_id=run_id
        )

        if run.status == 'completed':
            messages = await openai.beta.threads.messages.list(thread_id=self.thread.id)
            assistant_message = next(msg for msg in messages if msg.role == 'assistant')
            return assistant_message.content[0].text.value
        
        return None