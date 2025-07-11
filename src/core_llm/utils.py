import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from ollama import ChatResponse
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import configuration
from ..db.models import ChatSession

MEMORY_SIZE = configuration.MEMORY_SIZE  # Default memory size from configuration


def __split_content(
    response: ChatResponse,
) -> tuple[str, Optional[str]]:
    """
    Split the content of the response into main content and thinking content.
    """
    raw = response.message.content
    content = None
    thinking_content = None
    if '<think>' in raw and '</think>' in raw:
        # Extract thinking content if available
        thinking_content, content = raw.split("<think>\n")[-1].split("\n</think>\n\n")
    else:
        thinking_content = None
        content = raw
    return content, thinking_content


async def split_content_form_ollama(
    response: ChatResponse,
) -> tuple[str, Optional[str]]:
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        content, thinking_content = await loop.run_in_executor(
            pool,
            __split_content,
            response,
        )
    return content, thinking_content


async def get_chat_session_by_session_id(
    session: AsyncSession,
    user_id: int,
    chat_session_id: str,
) -> Optional[ChatSession]:
    try:
        query = select(
            ChatSession,
        ).where(
            ChatSession.user_id == user_id,
            ChatSession.session_id == chat_session_id,
        )
        result = await session.execute(query)
        chat_session = result.scalars().first()
        return chat_session
    except Exception as e:
        await session.rollback()
        raise e


async def update_chat_session(
    session: AsyncSession,
    chat_session: ChatSession,
    new_messages: list[dict],
) -> ChatSession:
    try:
        chat_session.messages.extend(new_messages)
        # Ensure we do not exceed the MEMORY_SIZE limit
        if len(chat_session.messages) > MEMORY_SIZE:
            chat_session.messages = chat_session.messages[-MEMORY_SIZE:]
        update_query = (
            update(ChatSession)
            .where(
                ChatSession.id == chat_session.id,
            )
            .values(
                messages=chat_session.messages,
            )
            .returning(ChatSession)
        )
        updated_chat_session = await session.execute(update_query)
        await session.commit()
        return updated_chat_session.scalars().first()
    except Exception as e:
        await session.rollback()
        raise e


async def create_chat_session(
    session: AsyncSession,
    user_id: int,
) -> ChatSession:
    try:
        query = (
            insert(ChatSession)
            .values(
                session_id=str(uuid.uuid4()),
                user_id=user_id,
                messages=[],
            )
            .returning(ChatSession)
        )
        new_chat_session = await session.execute(query)
        await session.commit()
        return new_chat_session.scalars().first()
    except Exception as e:
        await session.rollback()
        raise e
