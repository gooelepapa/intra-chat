from contextlib import asynccontextmanager

from fastapi import APIRouter, BackgroundTasks


@asynccontextmanager
async def lifespan(app: APIRouter):
    print("Starting up...")
    yield
    print("Shutting down...")


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
    from .service import run_fetchers

    background_tasks.add_task(run_fetchers)
    return {"message": "Fetchers started in the background."}


@router.post(
    '/ingest-articles-now',
    status_code=202,
)
async def ingest_articles_now(
    background_tasks: BackgroundTasks,
):
    from .service import ingest_articles

    background_tasks.add_task(ingest_articles)
    return {"message": "Ingesting articles started in the background."}
