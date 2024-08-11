import openai
from ..config import settings

class AIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    async def get_ai_response(self, message, customer_info):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful e-shop assistant."},
                {"role": "user", "content": f"Customer info: {customer_info}\nMessage: {message}"}
            ],
            stream=True
        )

        for chunk in response:
            if chunk['choices'][0]['delta'].get('content'):
                yield chunk['choices'][0]['delta']['content']