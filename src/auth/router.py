from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..common.schemas import MessageResponse
from ..db.session import get_db_session
from .schemas import RequestCreateUser, Token, TokenData
from .service import (
    auth_user,
    create_access_token,
    create_user,
    decode_access_token,
    get_user_by_account,
)

VERSION = "v1"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/auth/{VERSION}/login")

router = APIRouter(
    prefix=f"/auth/{VERSION}",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/register",
    response_model=MessageResponse,
)
async def user_register(
    user_data: RequestCreateUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    db_user = await get_user_by_account(session, user_data.account)
    if db_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already exists",
        )

    # Create the user in the database
    await create_user(session, user_data)
    return MessageResponse(code=201, message="User created successfully")


@router.post(
    "/login",
    response_model=Token,
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Token:
    try:
        user = await auth_user(session=session, account=form_data.username, password=form_data.password)
        access_token = await create_access_token(
            data={
                "id": user.id,
                "name": user.name,
                "account": user.account,
            }
        )
        return Token(access_token=access_token, token_type="bearer")
    except HTTPException as e:
        raise e
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during login: {str(e)}",
        )


@router.get(
    "/me",
    response_model=TokenData,
)
async def get_users(
    token: str = Depends(oauth2_scheme),
) -> TokenData:
    return await decode_access_token(token=token)
