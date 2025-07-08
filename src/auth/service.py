from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import configuration
from ..db.models import User
from .schemas import RequestCreateUser, TokenData
from .utils import get_hashed_password, verify_password

SECRET_KEY = configuration.SECRET_KEY
ALGORITHM = configuration.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = configuration.ACCESS_TOKEN_EXPIRE_MINUTES


async def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime().now(tz=UTC) + expires_delta
    else:
        expire = datetime.now(tz=UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    jwt_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_token


async def decode_access_token(
    token: str,
) -> TokenData | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        account: str = payload.get("account")
        if user_id is None or account is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(id=user_id, account=account)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while decoding the token: {str(e)}",
        )


async def create_user(
    session: AsyncSession,
    user: RequestCreateUser,
) -> User:
    try:
        hashed_pwd = await get_hashed_password(plain_password=user.password)
        insert_query = (
            insert(User)
            .values(
                name=user.name,
                account=user.account,
                email=user.email,
                password=hashed_pwd,
            )
            .returning(User)
        )
        new_user = await session.execute(insert_query)
        await session.commit()
        return new_user.scalars().first()
    except Exception as e:
        await session.rollback()
        raise e


async def get_user_by_account(
    session: AsyncSession,
    account: str,
) -> User | None:
    query = select(
        User.id,
        User.name,
        User.account,
        User.email,
        User.password,
    ).where(User.account == account)
    result = await session.execute(query)
    user_data = result.mappings().first()
    return User(**user_data) if user_data else None


async def auth_user(
    session: AsyncSession,
    account: str,
    password: str,
) -> User:
    user_in_db = await get_user_by_account(session, account)
    if not user_in_db:
        # User not found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if not await verify_password(plain_password=password, hashed_password=user_in_db.password):
        # Password verification failed
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect password",
        )
    return user_in_db
