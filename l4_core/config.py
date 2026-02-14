# l4_core/config.py

"""
Global Configuration (L4+)
--------------------------
Centralized application settings using pydantic-settings (Pydantic v2).

Features:
  - Environment-aware defaults
  - Strong typing for secrets and URLs
  - CORS configuration
  - AI provider keys
  - Database configuration
  - Future-proof for multi-tenant, multi-env, and feature flags
"""

from __future__ import annotations

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, AnyUrl



class Settings(BaseSettings):
    """
    Global application settings.
    Loaded from environment variables via pydantic-settings.
    """

    # ---------------------------------------------------------
    # ENVIRONMENT
    # ---------------------------------------------------------
    ENV: str = Field(
        "development",
        validation_alias="ENV",
        description="Application environment: development, staging, production",
    )

    # ---------------------------------------------------------
    # CORS
    # ---------------------------------------------------------
    CORS_ALLOW_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "*",  # Allow all during development
        ],
        description="Allowed CORS origins",
    )

    # ---------------------------------------------------------
    # AI PROVIDER KEYS
    # ---------------------------------------------------------
    OPENAI_API_KEY: str = Field("", validation_alias="OPENAI_API_KEY")
    DEEPSEEK_API_KEY: str = Field("", validation_alias="DEEPSEEK_API_KEY")
    ANTHROPIC_API_KEY: str = Field("", validation_alias="ANTHROPIC_API_KEY")
    GOOGLE_API_KEY: str = Field("", validation_alias="GOOGLE_API_KEY")

    # ---------------------------------------------------------
    # DATABASE
    # ---------------------------------------------------------
    DATABASE_URL: str = Field(
        "sqlite+aiosqlite:///./dev.db",
        validation_alias="DATABASE_URL",
        description="SQLAlchemy database URL",
    )

    # ---------------------------------------------------------
    # FUTURE: FEATURE FLAGS
    # ---------------------------------------------------------
    # Example:
    # ENABLE_AUDIT_ENGINE: bool = Field(True)
    # ENABLE_TEACHING_ENGINE: bool = Field(True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"




class Settings(BaseSettings):
    """
    Global application settings.
    Uses pydantic-settings (Pydantic v2) for .env loading.
    """

    # ---------------------------------------------------------
    # Environment
    # ---------------------------------------------------------
    ENV: str = Field("development", validation_alias="ENV")

    # ---------------------------------------------------------
    # CORS
    # ---------------------------------------------------------
    CORS_ALLOW_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "*",
    ]

    # ---------------------------------------------------------
    # AI Provider Keys
    # ---------------------------------------------------------
    OPENAI_API_KEY: str = Field("", validation_alias="OPENAI_API_KEY")
    DEEPSEEK_API_KEY: str = Field("", validation_alias="DEEPSEEK_API_KEY")
    ANTHROPIC_API_KEY: str = Field("", validation_alias="ANTHROPIC_API_KEY")
    GOOGLE_API_KEY: str = Field("", validation_alias="GOOGLE_API_KEY")

    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------
    DATABASE_URL: str = Field(
        "sqlite+aiosqlite:///./dev.db",
        validation_alias="DATABASE_URL"
    )

    # ---------------------------------------------------------
    # Audit
    # ---------------------------------------------------------
    ENABLE_AUDIT_ON_STARTUP: bool = Field(
        False,
        validation_alias="ENABLE_AUDIT_ON_STARTUP",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton settings instance
settings = Settings()

