import openai
from app.core.config import settings

openai.api_key = settings.OPENAI_API_KEY

class AIService:
    @staticmethod
    async def get_response(message: str, context: dict):
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful e-shop assistant."},
                    {"role": "user", "content": message}
                ],
                max_tokens=150
            )
            return response.choices[0].message['content']
        except Exception as e:
            print(f"Error in AI Service: {str(e)}")
            return "I'm sorry, I'm having trouble processing your request."