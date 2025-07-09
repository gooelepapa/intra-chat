import os

from pydantic_settings import BaseSettings, SettingsConfigDict

assert os.path.exists(".env"), "Configuration file '.env' not found. Please create it with the required settings."


class Configuration(BaseSettings):
    # DATABASE_URL = postgresql+asyncpg://chatuser:chatpass@localhost:5432/intra_chat
    # database arguments
    DATABASE_URL: str
    # Oauth2 arguments
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    # Ollama arguments
    MODEL: str
    MEMORY_SIZE: int = 100  # Default memory size for chat sessions

    model_config = SettingsConfigDict(env_file=".env")


configuration = Configuration()
