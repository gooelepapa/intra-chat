import asyncio
import csv
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

import aiofiles
from qdrant_client.models import PointStruct

from ..config import configuration
from .embedder import Embedder
from .logger import rag_logger
from .qdrant import get_qdrant_client


@dataclass
class DocumentChunk:
    source: str
    chunk_id: int
    text: str
    created_at: str

    def to_payload(self) -> dict:
        return {
            "source": self.source,
            "chunk_id": self.chunk_id,
            "text": self.text,
            "created_at": self.created_at,
        }


def __make_chunk(text: str, max_length: int = 200) -> List[str]:
    """
    Splits the text into chunks of a specified maximum length.
    """
    return [text[i : i + max_length] for i in range(0, len(text), max_length)]


async def chunk_text(text: str, max_length: int = 200) -> List[str]:
    """
    Asynchronously splits the text into chunks of a specified maximum length.
    """
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        chunks = await loop.run_in_executor(pool, __make_chunk, text, max_length)
    return chunks


async def read_txt(file_path: str) -> List[str]:
    """
    Reads a text file and returns its content as a list of strings.
    """
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as file:
        text = await file.read()
    chunked_text = await chunk_text(text)
    return chunked_text


async def read_csv(file_path: str) -> List[str]:
    """
    Reads a CSV file and returns its content as a list of strings.
    """
    results = []
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as file:
        content = await file.read()
        lines = content.splitlines()
        reader = csv.reader(lines)
        for row in reader:
            for col in row:
                results.extend(await chunk_text(col))
    return results


async def ingest_file(
    file_path: str,
    *,
    embedder: Optional[Embedder] = None,
):
    """
    Ingests a file and returns a list of PointStructs for Qdrant.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")
    if not file_path.endswith('.txt') and not file_path.endswith('.csv'):
        rag_logger.warning(f"Skipping unsupported file type: {file_path}")
        return
    if embedder is None:
        embedder = await Embedder.create()

    chunks = None
    if file_path.endswith('.txt'):
        chunks = await read_txt(file_path)
    elif file_path.endswith('.csv'):
        chunks = await read_csv(file_path)
    if not chunks:
        rag_logger.warning(f"No content to ingest from {file_path}")
        return

    timestamp = datetime.now().isoformat()
    file_name = os.path.basename(file_path)
    chunks = [
        DocumentChunk(
            source=file_name,
            chunk_id=i,
            text=chunk,
            created_at=timestamp,
        )
        for i, chunk in enumerate(chunks)
    ]

    texts = [chunk.text for chunk in chunks]
    embeddings = await embedder.embed_texts(texts)

    points = [
        PointStruct(
            id=str(uuid4()),
            vector=embedding,
            payload=chunk.to_payload(),
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]
    await get_qdrant_client().upsert(
        collection_name=configuration.QDRANT_COLLECTION,
        points=points,
    )
    rag_logger.debug(f"Ingested {len(points)} points from {file_path} into Qdrant.")


async def ingest_folder(folder_path: str):
    embedders = await Embedder.create()
    total = 0
    files = os.listdir(folder_path)
    rag_logger.info(f"Found {len(files)} files in folder {folder_path} for ingestion.")
    for file in files:
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and (file_path.endswith('.txt') or file_path.endswith('.csv')):
            await ingest_file(file_path, embedder=embedders)
        else:
            rag_logger.warning(f"Skipping non-file: {file_path}")
    rag_logger.info(f"Total {total} points ingested from folder.")


if __name__ == "__main__":
    # Test csv
    csv_file_path = 'month.csv'
    loop = asyncio.get_event_loop()
    chunks = loop.run_until_complete(read_csv(csv_file_path))
    print(chunks)
