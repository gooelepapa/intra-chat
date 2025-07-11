import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app="src.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"],
        log_level="info",
    )
