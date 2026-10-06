import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    ENVIRONMENT: str = Field(default="development")
    PORT: int = Field(default=8000)
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./ai_study.db")
    SUPABASE_URL: str = Field(default="")
    SUPABASE_KEY: str = Field(default="")
    GEMINI_API_KEY: str = Field(default="")
    SECRET_KEY: str = Field(default="dev-secret-ai-study-student-key-2026")
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://127.0.0.1:3000"])

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
