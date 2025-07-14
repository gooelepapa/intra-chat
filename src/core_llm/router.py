from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import get_current_user
from ..auth.schemas import TokenData
from ..db.session import get_db_session
from .llm_service import ask_llm, get_chat_session_detail, get_chat_session_list
from .schemas import (
    ChatSessionDetail,
    ChatSessionList,
    RequestChatMessage,
    ResponseChatMessage,
)

VERSION = 'v1'

router = APIRouter(
    prefix=f'/chat/{VERSION}',
    tags=['chat'],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    '/',
    response_model=List[ChatSessionList],
)
async def list_chat_sessions(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> List[ChatSessionList]:
    """
    List all chat sessions for the current user.
    """
    return await get_chat_session_list(
        session=db_session,
        current_user=current_user,
    )


@router.get(
    '/{chat_session_id}',
    response_model=ChatSessionDetail,
)
async def get_chat_session(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    chat_session_id: str,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ChatSessionDetail:
    """
    Get chat session details by `chat_session_id`.
    If the session with the given ID does not exist, it will raise a 404 error.
    """
    return await get_chat_session_detail(
        session=db_session,
        current_user=current_user,
        chat_session_id=chat_session_id,
    )


@router.post(
    '/ask',
    response_model=ResponseChatMessage,
)
async def ask_chat(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    request: RequestChatMessage,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResponseChatMessage:
    """
    Ask a question in a chat session.
    If `chat_session_id` is provided, it will use that session; otherwise, it
    will create a new session.
    """

    try:
        answer, thinking_content, chat_session_id = await ask_llm(
            session=db_session,
            request=request,
            current_user=current_user,
        )
        return ResponseChatMessage(
            code=200,
            content=answer,
            thinking=thinking_content,
            chat_session_id=chat_session_id,
        )
    except Exception as e:
        raise e
