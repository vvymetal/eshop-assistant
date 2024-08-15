from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "eShop Assistant"
    OPENAI_API_KEY: str
    ASSISTANT_ID: Optional[str] = None  # Changed from OPENAI_ASSISTANT_ID and made optional
    DATABASE_URL: Optional[str] = None  # Made optional
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"  # Default value added

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def ALLOWED_ORIGINS_LIST(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(',')]

settings = Settings()