"""Settings"""
import os

from pydantic import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_DIR = os.path.join(BASE_DIR, "..", "..")


class ChatService(BaseSettings):
    project_name: str
    host: str
    port: int


class Redis_conn(BaseSettings):
    host: str
    port: int


class TokenGroupView(BaseSettings):
    algo: str
    secret_key: str
    access_lifetime: int


class Settings(BaseSettings):
    chat_service: ChatService
    redis: Redis_conn
    token_group_view: TokenGroupView

    class Config:
        env_file = (
            os.path.join(ENV_DIR, ".env"),
            os.path.join(ENV_DIR, ".env.dev"),
        )
        env_nested_delimiter = "__"


settings = Settings()
