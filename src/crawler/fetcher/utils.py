import os
import re
from datetime import datetime, timedelta
from typing import List

import aiofiles
from playwright.async_api import Page
from pydantic import HttpUrl


def get_yesterday_date(fmt: str) -> str:
    """
    Returns the date of yesterday in the specified format.
    Args:
        fmt (str): The format string for the date.
    Returns:
        str: The date of yesterday.
    """
    return (datetime.now() - timedelta(days=1)).strftime(fmt)


async def auto_scroll(
    page: Page,
    *,
    max_scrolls: int = 10,
) -> None:
    """
    Automatically scrolls the page to the bottom until no new content is loaded or max_scrolls is reached.
    Args:
        page (Page): The Playwright page object.
        max_scrolls (int): Maximum number of scrolls to perform.
    Returns:
        None
    """
    previous = 0
    while max_scrolls > 0:
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1000)  # Wait for new content to load
        current_height = await page.evaluate("document.body.scrollHeight")
        if current_height == previous:
            break
        previous = current_height
        max_scrolls -= 1


async def fetch_news_content(
    page: Page,
    url: HttpUrl,
    query_selector: str,
    ads_keywords: List[str] = None,
) -> str:
    """
    Fetches the content of a news article from the given URL.
    Args:
        page (Page): The Playwright page object.
        url (str): The URL of the news article.
        query_selector (str): The CSS selector to find the content blocks.
        ads_keywords (List[str]): List of keywords to filter out ads.
    Returns:
        str: The full content of the article.
    """
    if ads_keywords is None:
        ads_keywords = []
    await page.goto(url.encoded_string())
    await auto_scroll(page)
    # Wait for new content to load
    content_block = await page.query_selector_all(query_selector)
    paragraphs = []
    for block in content_block:
        text = await block.inner_text()
        if any(keyword in text for keyword in ads_keywords):
            continue
        paragraphs.append(text.strip())
    full_content = "\n".join(p for p in paragraphs if p)
    return full_content


async def save_content_to_file(
    content: str,
    file_root: str,
    file_name: str,
) -> str:
    """
    Saves the content to a file, sanitizing the file path.
    Args:
        content (str): The content to save.
        file_path (str): The path where the content should be saved.
    Returns:
        str: The path to the saved file.
    """
    file_name = re.sub(r'[\\/*?:"<>|]', '_', file_name)  # Sanitize file name
    file_path = os.path.join(file_root, file_name)

    async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
        await f.write(content)

    return file_path
