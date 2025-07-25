from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import APIRouter, BackgroundTasks

from .logger import crawler_logger as logger
from .service import ingest_articles, run_fetchers

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: APIRouter):
    logger.info("Starting Crawler Scheduler")
    scheduler.add_job(
        run_fetchers,
        'cron',
        hour=0,
        minute=10,
        name='fetch_yesterday_articles',
    )
    logger.info("Scheduled job to fetch articles every day at 00:10")
    scheduler.add_job(
        ingest_articles,
        'cron',
        hour=0,
        minute=20,
        name='ingest_yesterday_articles',
    )
    logger.info("Scheduled job to ingest articles every day at 00:20")
    scheduler.start()
    yield
    logger.info("Stopping Crawler Scheduler")
    if scheduler.running:
        scheduler.shutdown(wait=True)
    logger.info("Crawler Scheduler stopped")


VERSION = 'v1'

router = APIRouter(
    prefix=f'/crawler/{VERSION}',
    tags=['crawler'],
    lifespan=lifespan,
)


@router.post(
    '/fetch-now',
    status_code=202,
)
async def fetch_now(
    background_tasks: BackgroundTasks,
):

    background_tasks.add_task(run_fetchers)
    return {"message": "Fetchers started in the background."}


@router.post(
    '/ingest-articles-now',
    status_code=202,
)
async def ingest_articles_now(
    background_tasks: BackgroundTasks,
):

    background_tasks.add_task(ingest_articles)
    return {"message": "Ingesting articles started in the background."}
