from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    APP_NAME: str = "Eshop Assistant"
    OPENAI_API_KEY: str
    DATABASE_URL: str
    ASSISTANT_ID: str
    PROJECT_NAME: str = "Eshop Assistant"
    ALLOWED_ORIGINS: Optional[List[AnyHttpUrl]]  # Use AnyHttpUrl for URL validation

    @validator("ALLOWED_ORIGINS", pre=True)
    def assemble_allowed_origins(cls, v: Optional[str]) -> Optional[List[AnyHttpUrl]]:
        if v is None or v.strip() == "":
            return []
        return [url.strip() for url in v.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "forbid"  # Forbid extra fields

settings = Settings()