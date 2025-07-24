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
    LLM_MODEL: str
    MEMORY_SIZE: int = 100  # Default memory size for chat sessions
    EMBED_MODEL: str = "qwen2:1.5b"  # Default embedding model
    # Qdrant arguments
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = None  # Optional API key for Qdrant
    QDRANT_COLLECTION: str = "rag_collection"
    # Crawler arguments
    CRAWLER_DATA_ROOT: str = "data/articles"
    # Ingested arguments
    INGESTED_ARTICLES: str = "ingested_articles"

    model_config = SettingsConfigDict(env_file=".env")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create folder if it does not exist
        if not os.path.exists(self.CRAWLER_DATA_ROOT):
            os.makedirs(self.CRAWLER_DATA_ROOT)
            print(f"Created directory: {self.CRAWLER_DATA_ROOT}")
        if not os.path.exists(self.INGESTED_ARTICLES):
            os.makedirs(self.INGESTED_ARTICLES)
            print(f"Created directory: {self.INGESTED_ARTICLES}")


configuration = Configuration()
