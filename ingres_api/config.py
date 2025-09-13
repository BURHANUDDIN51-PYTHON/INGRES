from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "INGRES Chatbot API"
    API_VERSION: str = "v1"
    DEBUG: bool = True

    # Example for API Keys or future secrets
    GEMINI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    class Config:
        env_file = str(Path(__file__).parent / ".env") # Reads variables from .env automatically
        env_file_encoding = "utf-8"

# Create a global settings instance
settings = Settings()
