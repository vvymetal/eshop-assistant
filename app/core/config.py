from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Eshop Assistant"
    OPENAI_API_KEY: str
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()