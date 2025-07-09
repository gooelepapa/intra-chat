from fastapi import APIRouter, Depends

from ..auth.dependencies import get_current_user
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
async def ask_chat(request: RequestChatMessage) -> ResponseChatMessage:

    try:
        answer, thinking_content = await ask_llm(request)
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
