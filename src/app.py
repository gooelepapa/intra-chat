from fastapi import FastAPI

from .model import router as model_router

app = FastAPI(
    root_path='/api',
)
app.include_router(model_router)


@app.get("/")
def read_root():
    return {"message": "Hello, uv + FastAPI!"}
