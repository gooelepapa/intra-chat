from fastapi import Depends

from .router import oauth2_scheme
from .service import decode_access_token


async def get_current_user(token: str = Depends(oauth2_scheme)):
    return await decode_access_token(token=token)  # type: ignore[return-value]
