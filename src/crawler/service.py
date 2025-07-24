import os
import shutil

from ..config import configuration
from ..rag.ingestor import ingest_folder
from .fetcher import get_fetchers
from .logger import crawler_logger as logger


async def run_fetchers():
    fetchers = get_fetchers()
    for fetcher in fetchers:
        try:
            logger.info(f"Running fetcher: {fetcher.__name__}")
            articles = await fetcher()
            logger.info(f"Fetcher {fetcher.__name__} fetched {len(articles)} articles.")
        except Exception as e:
            logger.error(f"Error running fetcher {fetcher.__name__}: {e}")


async def ingest_articles():
    """
    Ingest articles from the crawler data directory into the RAG system.
    """
    article_dir = configuration.CRAWLER_DATA_ROOT
    if not os.path.exists(article_dir):
        logger.warning(f"Article directory {article_dir} does not exist.")
        return
    logger.info(f"Ingesting articles from {article_dir}")
    await ingest_folder(article_dir)
    # Move articles to another directory to avoid conflicts
    processed_dir = configuration.INGESTED_ARTICLES
    os.makedirs(processed_dir, exist_ok=True)
    logger.info(f"Moving processed articles to {processed_dir}")
    shutil.move(article_dir, processed_dir)
