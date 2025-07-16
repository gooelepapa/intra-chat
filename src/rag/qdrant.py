from typing import Optional

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import CollectionStatus, Distance

from ..config import configuration
from .embedder import Embedder
from .logger import rag_logger

_qdrant_client: Optional[AsyncQdrantClient] = None
COLLECTION_NAME = configuration.QDRANT_COLLECTION
EMBEDDING_DIM: Optional[int] = None


async def ensure_collection():
    rag_embedder = await Embedder.create()

    global EMBEDDING_DIM
    EMBEDDING_DIM = rag_embedder.embedding_len
    assert EMBEDDING_DIM is not None, "Embedding dimension must be specified"

    collections = await _qdrant_client.get_collections()
    exists = any(collection.name == COLLECTION_NAME for collection in collections.collections)
    if not exists:
        rag_logger.info(f"Creating collection '{COLLECTION_NAME}' with dimension {EMBEDDING_DIM}")
        await _qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                "size": EMBEDDING_DIM,
                "distance": Distance.COSINE,
            },
        )


async def qdrant_status_check():
    info = await _qdrant_client.get_collection(COLLECTION_NAME)
    status = info.status
    if status != CollectionStatus.GREEN:
        rag_logger.warning(f"Collection '{COLLECTION_NAME}' status is {status}. Expected GREEN.")
    else:
        rag_logger.info(f"Collection '{COLLECTION_NAME}' is healthy with status {status}.")


def get_qdrant_client():
    """
    Returns the Qdrant client instance.
    This is useful for direct access to the client in other modules.
    """
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = AsyncQdrantClient(
            url=configuration.QDRANT_URL,
            api_key=configuration.QDRANT_API_KEY,
        )
    return _qdrant_client
