import jwt
from faker import Faker
from fastapi.exceptions import HTTPException

from core.config import settings


def verify_token_group_view(token: str, secret_key: str, algorithms: list):
    try:
        payload = jwt.decode(
            token, secret_key, algorithms=algorithms
        )
        return payload
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired")
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_token_group_view(user: str):
    access_token = jwt.encode(
        {"user_id": user, "exp": settings.token_group_view.access_lifetime},
        settings.token_group_view.secret_key,
        algorithm=settings.token_group_view.algo
    )
    return access_token


def get_user_and_token(cokies: dict, link: str):
    user = None
    if cokies.get("link"):
        payload = verify_token_group_view(token=cokies.get("link"),
                                          secret_key=settings.token_group_view.secret_key,
                                          algorithms=[settings.token_group_view.algo]
                                          )
        return payload.get("user_id"), cokies.get("link").decode('utf-8')
    if cokies.get("access_token"):
        payload = verify_token_group_view(token=cokies.get("access_token"),
                                          secret_key=settings.secret_key,
                                          algorithms=[settings.token.algo]
                                          )
        user = payload.get("user_id")
    if not user:
        user = Faker().first_name()
    token = create_token_group_view(user)
    return user, token.decode('utf-8')

