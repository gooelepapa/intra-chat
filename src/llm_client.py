from ollama import AsyncClient

_client = AsyncClient()


def get_client() -> AsyncClient:
    """
    Returns the global Ollama client instance.
    """
    return _client
