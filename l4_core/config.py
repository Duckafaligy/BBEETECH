# l4_core/config.py

from pydantic import BaseSettings, Field
from typing import List


class Settings(BaseSettings):
    # Environment
    ENV: str = Field("development", env="ENV")

    # CORS
    CORS_ALLOW_ORIGINS: List[str] = [
        "http://localhost:5173",   # Vite frontend
        "http://localhost:3000",   # React default
        "http://127.0.0.1:5173",
        "*",                       # Allow all during development
    ]

    # AI Keys
    OPENAI_API_KEY: str = Field("", env="OPENAI_API_KEY")
    DEEPSEEK_API_KEY: str = Field("", env="DEEPSEEK_API_KEY")
    ANTHROPIC_API_KEY: str = Field("", env="ANTHROPIC_API_KEY")
    GOOGLE_API_KEY: str = Field("", env="GOOGLE_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
