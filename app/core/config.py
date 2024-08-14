from pydantic_settings import BaseSettings
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    APP_NAME: str = "Eshop Assistant"
    OPENAI_API_KEY: str
    DATABASE_URL: str
    ASSISTANT_ID: str
    PROJECT_NAME: str = "Eshop Assistant"
    ALLOWED_ORIGINS: Union[List[AnyHttpUrl], str]  # Allow List of URLs or a wildcard string

    @validator("ALLOWED_ORIGINS", pre=True)
    def assemble_allowed_origins(cls, v: Optional[str]) -> Union[List[AnyHttpUrl], str]:
        if v is None or v.strip() == "":
            return []
        if v == "*":
            return v
        return [url.strip() for url in v.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "forbid"  # Forbid extra fields

settings = Settings()