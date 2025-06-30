from contextlib import asynccontextmanager

from fastapi import FastAPI

from .model import router as model_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI to pull models at startup.
    """
    from .model.llm import pull_model

    # Pull the models when the application starts
    await pull_model()
    yield
    # Cleanup can be done here if needed


app = FastAPI(
    title="Intra Chat API",
    root_path='/api',
    lifespan=lifespan,
)
app.include_router(model_router)


@app.get("/")
def read_root():
    return {"message": "Hello, uv + FastAPI!"}
