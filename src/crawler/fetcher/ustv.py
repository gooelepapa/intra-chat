import os
from typing import List

from playwright.async_api import async_playwright

from ...config import configuration
from ..schemas import NewsArticle
from .logger import fetcher_logger as logger
from .utils import (
    auto_scroll,
    fetch_news_content,
    get_yesterday_date,
    save_content_to_file,
)

ARTICLE_DIR = f"{configuration.CRAWLER_DATA_ROOT}/ustv"


async def crawl_ustv() -> List[NewsArticle]:

    article_data: List[NewsArticle] = []

    yesterday = get_yesterday_date(fmt="%Y-%m-%d")
    article_dir = f"{ARTICLE_DIR}/{yesterday}"
    os.makedirs(article_dir, exist_ok=True)
    logger.info(f"Fetching USTV articles for {yesterday}")
    url = f"https://news.ustv.com.tw/newslist/146?startDate={yesterday}&endDate={yesterday}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await auto_scroll(page)
        # Wait for list
        articles = await page.query_selector_all("#newslist .media")
        for article in articles:
            title_el = await article.query_selector(".subject")
            title = await title_el.inner_text()
            href = await title_el.get_attribute("href")

            article_data.append(
                NewsArticle(
                    title=title,
                    url=href,
                    source="USTV",
                    content="",  # Content will be fetched later
                )
            )
        logger.info(f"Found {len(article_data)} articles for {yesterday}")
        for article in article_data:
            if article.url:
                full_content = await fetch_news_content(
                    page,
                    article.url,
                    "p.block_text",
                    ["ustvshop"],
                )
                file_path = await save_content_to_file(
                    content=full_content,
                    file_root=article_dir,
                    file_name=f"{article.title}.txt",
                )
                article.content = full_content
                logger.info(f"Saved article: {article.title} to {file_path}")
        await browser.close()
        return article_data
