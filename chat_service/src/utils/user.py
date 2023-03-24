import jwt
from faker import Faker
from fastapi.exceptions import HTTPException

from core.config import settings


def verify_token_group_view(token: str, secret_key: str, algorithms: list):
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithms)
        return payload
    except jwt.exceptions.ExpiredSignatureError:
        return None
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_token_group_view(user: str):
    access_token = jwt.encode(
        {"user_id": user, "exp": settings.token_group_view.access_lifetime},
        settings.token_group_view.secret_key,
        algorithm=settings.token_group_view.algo,
    )
    return access_token


def get_user_and_token(params: dict, link: str):
    user = None
    if params.get(link):
        payload = verify_token_group_view(
            token=params.get(link),
            secret_key=settings.token_group_view.secret_key,
            algorithms=[settings.token_group_view.algo],
        )
        if payload:
            return payload.get("user_id"), params.get(link).decode("utf-8")
    if params.get("access_token"):
        payload = verify_token_group_view(
            token=params.get("access_token"),
            secret_key=settings.secret_key,
            algorithms=[settings.token.algo],
        )
        if payload:
            user = payload.get("user_id")
    if not user:
        user = Faker().first_name()
    token = create_token_group_view(user)
    return user, token.decode("utf-8")
