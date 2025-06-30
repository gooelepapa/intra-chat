from typing import Tuple

from ollama import AsyncClient, ChatResponse

from .logger import model_logger
from .schemas import RequestChatMessage

client = AsyncClient()

test_memory = {}


async def pull_model() -> None:
    """
    Pull the Qwen 3 model from Ollama.
    """
    models = await client.list()
    if "qwen3:8b" not in models:
        model_logger.info("Pulling Qwen 3 model...")
        await client.pull("qwen3:8b")
        model_logger.info("Qwen 3 model pulled successfully.")
    if "gemma3:4b" not in models:
        model_logger.info("Pulling Gemma 3 model...")
        await client.pull("gemma3:4b")
        model_logger.info("Gemma 3 model pulled successfully.")


def post_process_response(model: str, response: ChatResponse) -> Tuple[str, str]:
    raw_content = response.message.content
    content = None
    thinking_content = None
    if model == "qwen3:8b":
        thinking_content, content = raw_content.split("<think>\n")[-1].split("\n</think>\n\n")
    elif model == "gemma3:4b":
        thinking_content = None
        content = raw_content
    else:
        raise ValueError(f"Unsupported model: {model}")
    return content, thinking_content


async def ask_llm(request: RequestChatMessage) -> str:
    # Get the user ID from the request
    user_id = request.user_id
    user_content = request.content
    # If the user ID is not in the test memory, initialize it
    if user_id not in test_memory:
        test_memory[user_id] = []
    history_messages = test_memory[user_id]
    # Call the Qwen 3 model with the user's message
    # model = "qwen3:8b"
    # model = "gemma3:4b"
    response = await client.chat(
        model="qwen3:8b",
        messages=[*history_messages, {'role': 'user', 'content': user_content}],
    )
    # Append the model's response to the memory
    test_memory[user_id].append(
        {
            'role': 'user',
            'content': user_content,
        }
    )
    test_memory[user_id].append(
        {
            'role': 'assistant',
            'content': response["message"]["content"],
        }
    )
    # Return the model's response content
    return post_process_response("qwen3:8b", response)
