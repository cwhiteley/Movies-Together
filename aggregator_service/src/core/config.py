"""Settings"""
import os

from pydantic import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_DIR = os.path.join(BASE_DIR, "..", "..")


class BaseApi(BaseSettings):
    project_name: str
    host: str
    port: int


class ChatService(BaseSettings):
    project_name: str
    host: str
    port: int


class VideoService(BaseSettings):
    project_name: str
    host: str
    port: int


class Redis(BaseSettings):
    host: str
    port: int


class ApiKeys(BaseSettings):
    omdb: str


class Token(BaseSettings):
    access_lifetime: int
    refresh_lifetime: int
    algo: str


class TokenGroupView(BaseSettings):
    algo: str
    secret_key: str
    access_lifetime: int


class Settings(BaseSettings):
    server_host: str
    secret_key: str

    token: Token
    token_group_view: TokenGroupView
    base_api: BaseApi
    chat_service: ChatService
    video_service: VideoService
    redis: Redis
    api_keys: ApiKeys
    debug: str

    class Config:
        env_file = (
            os.path.join(ENV_DIR, ".env"),
            os.path.join(ENV_DIR, ".env.dev"),
        )
        env_nested_delimiter = "__"


settings = Settings()

if settings.debug == "True":
    ROOT_PATH = ""
else:
    ROOT_PATH = "./src/"
