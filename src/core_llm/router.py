from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import get_current_user
from ..auth.schemas import TokenData
from ..db.session import get_db_session
from .llm_service import ask_llm
from .schemas import RequestChatMessage, ResponseChatMessage

VERSION = 'v1'

router = APIRouter(
    prefix=f'/chat/{VERSION}',
    tags=['chat'],
    dependencies=[Depends(get_current_user)],
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
