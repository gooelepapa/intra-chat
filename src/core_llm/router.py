from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import get_current_user
from ..db.session import get_db_session
from .llm import ask_llm
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
    request: Annotated[RequestChatMessage, Depends()],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ResponseChatMessage:

    try:
        answer, thinking_content = await ask_llm(session=session, request=request)
        return ResponseChatMessage(
            code=200,
            content=answer,
            thinking=thinking_content,
        )
    except Exception as e:
        return ResponseChatMessage(
            code=500,
            content=f'Error: {str(e)}',
        )
