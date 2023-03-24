import jwt
from fastapi import Request, Cookie
from fastapi.exceptions import HTTPException

from core.config import settings


async def verify_token(request: Request, access_token: str = Cookie(None)):
    try:
        payload = jwt.decode(
            access_token, settings.secret_key, algorithms=[settings.token.algo]
        )
        print("Access token verified")
        return payload
    except jwt.exceptions.ExpiredSignatureError:
        print("Access token expired")
        raise HTTPException(status_code=401, detail="Access token expired")
    except jwt.exceptions.DecodeError:
        print("Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")
