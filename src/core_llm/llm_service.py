from typing import Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.schemas import TokenData
from ..auth.service import get_user_by_id
from ..config import configuration
from ..db.models import ChatSession
from ..llm_client import get_client
from ..rag.retriever import Retriever
from .logger import model_logger
from .schemas import ChatSessionDetail, ChatSessionList, RequestChatMessage
from .utils import (
    create_chat_session,
    query_chat_session_by_session_id,
    query_chat_sessions,
    split_content_form_ollama,
    update_chat_session,
)

rag_retriever = Retriever(embedder=None)  # Lazy initialization of the retriever

MODEL = configuration.LLM_MODEL  # Default model name from configuration
# MODEL = "gemma3:4b"  # Uncomment to use Gemma 3 model
# MODEL = "qwen3:8b"  # Default model name


async def pull_model() -> None:
    """
    Pull the MODEL from Ollama.
    """
    models = await get_client().list()
    model_names = [m["model"] for m in models["models"]]
    if MODEL not in model_names:
        model_logger.info(f"Pulling {MODEL} model...")
        await get_client().pull(MODEL)
        model_logger.info(f"{MODEL} model pulled successfully.")


async def warmup_model() -> None:
    """
    Warm up the llm models by making a test request.
    """
    try:
        model_logger.info(f"Warming up {MODEL} model...")
        await get_client().chat(
            model=MODEL,
            messages=[{'role': 'user', 'content': 'Warmup, answer short as possible as you can.'}],
        )
        model_logger.info(f"{MODEL} model warmed up successfully.")
    except Exception as e:
        model_logger.error(f"Error warming up {MODEL} model: {e}")


async def __user_check(
    session: AsyncSession,
    user_id: str,
) -> None:
    """
    Check if the user exists in the database.
    Raises HTTPException if the user does not exist.
    """
    user = await get_user_by_id(session=session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )


async def __get_chat_session_by_id(
    session: AsyncSession,
    user_id: str,
    chat_session_id: Optional[str],
) -> Optional[ChatSession]:
    if chat_session_id is None:
        # Create a new chat session if chat_session_id is None
        chat_session = await create_chat_session(
            session=session,
            user_id=user_id,
        )
    else:
        # Get the chat memory for the user
        chat_session = await query_chat_session_by_session_id(
            session=session,
            user_id=user_id,
            chat_session_id=chat_session_id,
        )
    return chat_session


async def ask_llm(
    session: AsyncSession,
    request: RequestChatMessage,
    current_user: TokenData,
) -> Tuple[str, Optional[str], str]:
    user_id = current_user.id
    user_name = current_user.name
    user_content = request.content
    chat_session_id = request.chat_session_id
    # Check user existence
    await __user_check(session=session, user_id=user_id)

    chat_session = await __get_chat_session_by_id(
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
    message = [
        {"role": "system", "content": "你是一位台股與科技新聞的助理，所有的回答請保持簡潔，只補充適當的資訊。"},
        *history_messages,
        {"role": "user", "content": user_content},
    ]
    llm_response = await get_client().chat(
        model=MODEL,
        messages=message,
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


async def ask_llm_with_rag(
    session: AsyncSession,
    request: RequestChatMessage,
    current_user: TokenData,
) -> Tuple[str, Optional[str], str]:
    user_id = current_user.id
    user_name = current_user.name
    user_content = request.content
    chat_session_id = request.chat_session_id

    # Check user existence
    await __user_check(session=session, user_id=user_id)

    chat_session = await __get_chat_session_by_id(
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

    # Search qdrant for relevant documents
    rag_results = await rag_retriever.search(query=user_content, top_k=5)

    # Combine the user's message with the RAG results
    context_text = "\n".join(f"({i + 1}) {r.payload.get('text', '')}" for i, r in enumerate(rag_results))
    rag_messages = [
        {
            "role": "system",
            "content": f"你是一位台股與科技新聞的助理，所有的回答請保持簡潔，只補充適當的資訊。以下是與問題相關的資料：\n{context_text}",
        },
        *chat_session.messages,
        {"role": "user", "content": user_content},
    ]
    # 4. 呼叫 LLM
    llm_response = await get_client().chat(
        model=MODEL,
        messages=rag_messages,
    )
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


async def get_chat_session_list(
    session: AsyncSession,
    current_user: TokenData,
) -> list:
    chat_sessions = await query_chat_sessions(
        session=session,
        user_id=current_user.id,
    )
    return [
        ChatSessionList(
            session_id=chat_session.session_id,
            created_at=chat_session.created_at.isoformat(),
        )
        for chat_session in chat_sessions
    ]


async def get_chat_session_detail(
    session: AsyncSession,
    current_user: TokenData,
    chat_session_id: str,
) -> ChatSessionDetail:
    chat_session = await query_chat_session_by_session_id(
        session=session,
        user_id=current_user.id,
        chat_session_id=chat_session_id,
    )
    if not chat_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session with ID {chat_session_id} not found for User: {current_user.name}.",
        )
    return ChatSessionDetail(
        session_id=chat_session.session_id,
        created_at=chat_session.created_at.isoformat(),
        messages=chat_session.messages,
    )
