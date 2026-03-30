"""Configuration management for PromptGym using pydantic-settings."""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    LLM_MODE: str = "mock"  # "mock" | "openai" | "together"
    MAX_STEPS: int = 5
    REWARD_THRESHOLD: float = 0.95
    HOST: str = "0.0.0.0"
    PORT: int = 7860
    LOG_FILE: str = "logs/episodes.jsonl"
    USE_TORCH_SCORER: bool = False
    OPENAI_API_KEY: Optional[str] = None
    TOGETHER_API_KEY: Optional[str] = None


# Singleton instance
settings = Settings()
