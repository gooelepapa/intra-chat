from pydantic import BaseModel


class MessageResponse(BaseModel):
    # For api basic response
    code: int
    message: str

    model_config = {
        "json_schema_extra": {
            "example": [
                {"code": 200, "message": "Success"},
                {"code": 400, "message": "User already exists"},
                {"code": 404, "message": "Not Found"},
            ],
        },
    }
