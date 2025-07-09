from typing import Optional

from pydantic import BaseModel


class RequestChatMessage(BaseModel):
    user_id: int
    chat_session_id: Optional[str] = None
    content: str


class ResponseChatMessage(BaseModel):
    code: int
    thinking: Optional[str] = None
    content: str
