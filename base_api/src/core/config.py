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


class Settings(BaseSettings):
    server_host: str
    base_api: BaseApi
    chat_service: ChatService
    video_service: VideoService
    redis: Redis
    api_keys: ApiKeys

    class Config:
        env_file = (
            os.path.join(ENV_DIR, ".env"),
            os.path.join(ENV_DIR, ".env.dev"),
        )
        env_nested_delimiter = "__"


settings = Settings()
