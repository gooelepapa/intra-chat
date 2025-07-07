import asyncio
from concurrent.futures import ThreadPoolExecutor

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def __hash_pwd(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


async def get_hashed_password(plain_password: str) -> str:
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        hashed_password = await loop.run_in_executor(pool, __hash_pwd, plain_password)
    return hashed_password


def __verify_pwd(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        is_verified = await loop.run_in_executor(pool, __verify_pwd, plain_password, hashed_password)
    return is_verified
