from fastapi import HTTPException, status
from ollama import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.schemas import TokenData
from ..auth.service import get_user_by_id
from ..config import configuration
from .logger import model_logger
from .schemas import RequestChatMessage
from .utils import (
    create_chat_session,
    get_chat_session_by_session_id,
    split_content_form_ollama,
    update_chat_session,
)

client = AsyncClient()

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


async def ask_llm(
    session: AsyncSession,
    request: RequestChatMessage,
    current_user: TokenData,
) -> str:
    user_id = current_user.id
    user_name = current_user.name
    user_content = request.content
    chat_session_id = request.chat_session_id
    # Check user existence
    user = await get_user_by_id(session=session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )

    chat_session = None
    # Create a new chat session if chat_session_id is None
    if chat_session_id is None:
        chat_session = await create_chat_session(
            session=session,
            user_id=user_id,
        )
    else:
        # Get the chat memory for the user
        chat_session = await get_chat_session_by_session_id(
            session=session,
            user_id=user_id,
            chat_session_id=chat_session_id,
        )
    # If chat_session is still None, it means user give an invalid chat_session_id.
    if chat_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session with ID {chat_session_id} not found for User: {user_name}.",
        )
    # Call the llm model with the user's message
    history_messages = chat_session.messages
    llm_response = await client.chat(
        model=MODEL,
        messages=[*history_messages, {'role': 'user', 'content': user_content}],
    )
    # Append the model's response to the chat session
    new_message = [
        {
            'role': 'user',
            'content': user_content,
        },
        {
            'role': 'assistant',
            'content': llm_response.message.content,
        },
    ]
    await update_chat_session(
        session=session,
        chat_session=chat_session,
        new_messages=new_message,
    )
    # Return the model's response content
    content, thinking_content = await split_content_form_ollama(llm_response)

    return content, thinking_content, chat_session.session_id
