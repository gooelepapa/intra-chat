from typing import Optional

from pydantic import BaseModel


class ChatSessionList(BaseModel):
    session_id: str
    created_at: str

    model_config = {
        "json_schema_extra": {
            "example": [
                {
                    "session_id": "35409181-4de1-4867-beda-adadd9eb3835",
                    "created_at": "2023-10-01T12:00:00Z",
                },
                {
                    "session_id": "12345678-4de1-4867-beda-adadd9eb3835",
                    "created_at": "2023-10-02T12:00:00Z",
                },
            ]
        },
    }


class ChatSessionDetail(BaseModel):
    session_id: str
    created_at: str
    messages: list[dict]

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "35409181-4de1-4867-beda-adadd9eb3835",
                "created_at": "2023-10-01T12:00:00Z",
                "messages": [
                    {"role": "user", "content": "Hello, how are you?"},
                    {"role": "assistant", "content": "I'm doing well, thank you!"},
                ],
            }
        },
    }


class RequestChatMessage(BaseModel):
    chat_session_id: Optional[str] = None
    content: str

    model_config = {
        "json_schema_extra": {
            "example": [
                {
                    "chat_session_id": "35409181-4de1-4867-beda-adadd9eb3835",
                    "content": "Hello, how are you?",
                },
                {
                    "chat_session_id": None,
                    "content": "What is the weather like today?",
                },
            ]
        },
    }


class ResponseChatMessage(BaseModel):
    code: int
    chat_session_id: str
    thinking: Optional[str] = None
    content: str

    model_config = {
        "json_schema_extra": {
            "example": [
                {
                    "code": 200,
                    "chat_session_id": "35409181-4de1-4867-beda-adadd9eb3835",
                    "thinking": "Thinking about the user's greeting.",
                    "content": "I'm doing well, thank you! How can I assist you today?",
                },
                {
                    "code": 200,
                    "chat_session_id": "35409181-4de1-4867-beda-adadd9eb3835",
                    "thinking": None,
                    "content": "Error: Unable to process the request.",
                },
            ]
        }
    }
