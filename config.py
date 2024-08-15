from pydantic_settings import BaseSettings
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    APP_NAME: str = "Eshop Assistant"
    OPENAI_API_KEY: str
    DATABASE_URL: str
    ASSISTANT_ID: str
    PROJECT_NAME: str = "Eshop Assistant"
    ALLOWED_ORIGINS: Union[List[AnyHttpUrl], str]  # Allow either a list of URLs or a string

    @validator("ALLOWED_ORIGINS", pre=True)
    def assemble_allowed_origins(cls, v: Union[str, List]) -> Union[List[AnyHttpUrl], str]:
        if isinstance(v, str) and v.strip() == "*":
            return v
        if isinstance(v, str):
            return [url.strip() for url in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "forbid"  # Forbid extra fields

settings = Settings()