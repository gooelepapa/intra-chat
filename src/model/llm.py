from typing import Tuple

from ollama import AsyncClient, ChatResponse

from ..config import configuration
from .logger import model_logger
from .schemas import RequestChatMessage

client = AsyncClient()

test_memory = {}
MODEL = configuration.MODEL  # Default model name from configuration
# MODEL = "gemma3:4b"  # Uncomment to use Gemma 3 model
# MODEL = "qwen3:8b"  # Default model name


async def pull_model() -> None:
    """
    Pull the MODEL from Ollama.
    """
    models = await client.list()
    if MODEL not in models:
        model_logger.info(f"Pulling {MODEL} model...")
        await client.pull(MODEL)
        model_logger.info(f"{MODEL} model pulled successfully.")


async def warmup_model() -> None:
    """
    Warm up the llm models by making a test request.
    """
    try:
        model_logger.info(f"Warming up {MODEL} model...")
        await client.chat(
            model=MODEL,
            messages=[{'role': 'user', 'content': 'Warmup, answer short as possible as you can.'}],
        )
        model_logger.info(f"{MODEL} model warmed up successfully.")
    except Exception as e:
        model_logger.error(f"Error warming up {MODEL} model: {e}")


def post_process_response(response: ChatResponse) -> Tuple[str, str]:
    raw_content = response.message.content
    content = None
    thinking_content = None
    if '<think>' in raw_content and '</think>' in raw_content:
        # Extract thinking content if available
        thinking_content, content = raw_content.split("<think>\n")[-1].split("\n</think>\n\n")
    else:
        thinking_content = None
        content = raw_content
    return content, thinking_content


async def ask_llm(request: RequestChatMessage) -> str:
    # Get the user ID from the request
    user_id = request.user_id
    user_content = request.content
    # If the user ID is not in the test memory, initialize it
    if user_id not in test_memory:
        test_memory[user_id] = []
    history_messages = test_memory[user_id]
    # Call the llm model with the user's message
    response = await client.chat(
        model=MODEL,
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
    return post_process_response(response)
