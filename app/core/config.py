from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "E-shop Assistant"
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]  # Přidejte další origins podle potřeby
    OPENAI_API_KEY: str
    ASSISTANT_ID: str
    ANTHROPIC_API_KEY: str
    DEFAULT_AI_MODEL: str

    class Config:
        env_file = ".env"

settings = Settings()

