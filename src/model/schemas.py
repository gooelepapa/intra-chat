from typing import Optional

from pydantic import BaseModel


class RequestChatMessage(BaseModel):
    user_id: str
    content: str


class ResponseChatMessage(BaseModel):
    code: int
    thinking: Optional[str] = None
    content: str
    content: str
