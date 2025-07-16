from contextlib import asynccontextmanager

from fastapi import FastAPI

from .auth import router as auth_router
from .core_llm import router as llm_router
from .core_llm.llm_service import pull_model, warmup_model
from .db.models import Base
from .db.session import engine
from .rag.qdrant import ensure_collection, get_qdrant_client, qdrant_status_check


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI to pull models at startup.
    """

    # Pull the models when the application starts
    await pull_model()
    await warmup_model()
    await ensure_collection()
    await qdrant_status_check()
    async with engine.begin() as conn:
        # Ensure the database is created
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup can be done here if needed
    qdrant = get_qdrant_client()
    if qdrant:
        await qdrant.close()
    await engine.dispose()


app = FastAPI(
    title="Intra Chat API",
    root_path='/api',
    lifespan=lifespan,
)
app.include_router(llm_router)
app.include_router(auth_router)


@app.get("/")
def read_root():
    return {"message": "Hello, uv + FastAPI!"}
