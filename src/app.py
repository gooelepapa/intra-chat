from contextlib import asynccontextmanager

from fastapi import FastAPI

from .auth import router as auth_router
from .db.models import Base
from .db.session import engine
from .model import router as model_router
from .model.llm import pull_model, warmup_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI to pull models at startup.
    """

    # Pull the models when the application starts
    await pull_model()
    await warmup_model()
    async with engine.begin() as conn:
        # Ensure the database is created
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup can be done here if needed
    await engine.dispose()


app = FastAPI(
    title="Intra Chat API",
    root_path='/api',
    lifespan=lifespan,
)
app.include_router(model_router)
app.include_router(auth_router)


@app.get("/")
def read_root():
    return {"message": "Hello, uv + FastAPI!"}
