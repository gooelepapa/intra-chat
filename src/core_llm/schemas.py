from typing import Optional

from pydantic import BaseModel


class RequestChatMessage(BaseModel):
    chat_session_id: Optional[str] = None
    content: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "chat_session_id": "35409181-4de1-4867-beda-adadd9eb3835",
                "content": "Hello, how are you?",
            },
        },
    }


class ResponseChatMessage(BaseModel):
    code: int
    thinking: Optional[str] = None
    content: str

    model_config = {
        "json_schema_extra": {
            "example": [
                {
                    "code": 200,
                    "thinking": "Thinking about the user's greeting.",
                    "content": "I'm doing well, thank you! How can I assist you today?",
                },
                {
                    "code": 200,
                    "thinking": None,
                    "content": "Error: Unable to process the request.",
                },
            ]
        }
    }
