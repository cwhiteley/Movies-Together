import os
from logging import config as logging_config

from core.logger import LOGGING
from pydantic import BaseModel, BaseSettings

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_DIR = os.path.join(BASE_DIR, "..", "..")


class ElasticIndexes(BaseModel):
    genre: str
    person: str
    filmwork: str


class ElasticSettings(BaseModel):
    site: str
    port: int
    index: ElasticIndexes


class RedisSettings(BaseModel):
    host: str
    port: int


class Settings(BaseSettings):
    project_name: str
    page_size: int

    elastic: ElasticSettings
    redis: RedisSettings

    class Config:
        env_file = (
            os.path.join(ENV_DIR, ".env"),
            os.path.join(ENV_DIR, ".env.dev"),
        )
        env_nested_delimiter = "__"


settings = Settings()
