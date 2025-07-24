from typing import Callable, List

from ..schemas import NewsArticle
from .ustv import crawl_ustv

# For type hinting
FetcherFunction = Callable[[], List[NewsArticle]]


def get_fetchers() -> List[FetcherFunction]:
    """
    Returns a list of fetcher functions.
    """
    return [
        crawl_ustv,
        # Add other fetcher functions here as needed
    ]
