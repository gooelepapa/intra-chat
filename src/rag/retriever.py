from dataclasses import dataclass
from typing import List, Optional

from qdrant_client.http.models import SearchParams

from ..config import configuration
from .embedder import Embedder
from .qdrant import get_qdrant_client


@dataclass
class SearchResult:
    id: str
    score: float
    payload: dict


class Retriever:
    def __init__(
        self,
        *,
        collection_name: str = configuration.QDRANT_COLLECTION,
        embedder: Optional[Embedder] = None,
        top_k: int = 5,
    ):
        self.collection_name = collection_name
        self.embedder = embedder
        self.top_k = top_k
        self.qdrant_client = get_qdrant_client()

    async def search(
        self,
        query: str,
        top_k: Optional[int] = None,
    ) -> List[SearchResult]:
        if self.embedder is None:
            self.embedder = await Embedder.create()
        if top_k is None:
            top_k = self.top_k
        query_vector = await self.embedder.embed_texts([query])
        results = await self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_vector[0],
            limit=top_k,
            search_params=SearchParams(
                exact=True,  # Use exact search for better accuracy
                hnsw_ef=128,  # Higher ef for better recall
            ),
        )
        return [SearchResult(id=hit.id, score=hit.score, payload=hit.payload) for hit in results]
