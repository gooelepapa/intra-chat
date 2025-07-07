from pydantic import BaseModel, EmailStr, Field


class RequestCreateUser(BaseModel):
    name: str = Field(..., max_length=50)
    account: str = Field(..., max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=256)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "John Doe",
                "account": "johndoe",
                "email": "johndoe@example.com",
                "password": "securepassword",
            },
        },
    }


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    id: int
    account: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "account": "johndoe",
            },
        },
    }
