import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    max_pages: int = 5
    max_chars_per_page: int = 2000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()


def require_openai_key() -> str:
    key = settings.openai_api_key or os.getenv("OPENAI_API_KEY", "")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not set. Create a .env file (see .env.example).")
    return key
