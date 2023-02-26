"""Settings"""
import os

from pydantic import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_DIR = os.path.join(BASE_DIR, "..", "..")


class BaseApi(BaseSettings):
    project_name: str
    host: str
    port: int


class Redis(BaseSettings):
    host: str
    port: int


class Settings(BaseSettings):
    base_api: BaseApi
    redis: Redis

    class Config:
        env_file = (os.path.join(ENV_DIR, ".env.example"), os.path.join(ENV_DIR, ".env.example.dev"))
        env_nested_delimiter = "__"


settings = Settings()
