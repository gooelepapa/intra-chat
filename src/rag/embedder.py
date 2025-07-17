import asyncio
from typing import List

from ..config import configuration
from ..llm_client import get_client
from .logger import rag_logger


class Embedder:
    """
    A class to handle text embedding using the configured embedding model.
    Create an instance using the `Embedder.create()` method to ensure the model is pulled and ready for use.
    """

    def __init__(self):
        self.model = configuration.EMBED_MODEL
        self.client = get_client()
        self.embedding_len = None

    @classmethod
    async def create(cls) -> 'Embedder':
        """
        Factory method to create an instance of Embedder.
        This can be used to ensure the model is pulled before embedding.
        """
        embedder = cls()
        await embedder.__pull_model()
        embedder.embedding_len = await embedder.__get_embedding_len()
        return embedder

    async def __get_embedding_len(self) -> int:
        """
        Get the length of the embedding vector for the configured model.
        This is useful to ensure consistency in embedding dimensions.
        """
        response = await self.client.embeddings(model=self.model, prompt="test")
        return len(response.embedding)

    async def __pull_model(self) -> None:
        """
        Pull the embedding model from Ollama if it is not already available.
        """
        models = await self.client.list()
        model_names = [m["model"] for m in models["models"]]
        if self.model not in model_names:
            rag_logger.info(f"Pulling {self.model} model...")
            await self.client.pull(self.model)
            rag_logger.info(f"{self.model} model pulled successfully.")

    async def __embed_single(self, text: str) -> List[float]:
        """
        Embed a single text using the configured embedding model.
        """
        response = await self.client.embeddings(model=self.model, prompt=text)
        return response.embedding

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts using the configured embedding model."""
        tasks = [self.__embed_single(text) for text in texts]
        embeddings = await asyncio.gather(*tasks)
        return embeddings


if __name__ == "__main__":
    # Quick test to ensure the embedder works
    texts = ["男生", "女生", "雄性動物", "雌性動物"]
    embedder = asyncio.run(Embedder.create())
    embeddings = asyncio.run(embedder.embed_texts(texts))
    print(len(embeddings), len(embeddings[0]))  # 應該是 (4, 1536)
