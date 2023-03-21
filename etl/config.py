import os

from pydantic import BaseSettings, BaseModel

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_DIR = os.path.join(BASE_DIR)


class PostgresSettings(BaseModel):
    dbname: str
    user: str
    password: str
    host: str
    port: int


class ElasticSettings(BaseModel):
    site: str
    port: int


class Settings(BaseSettings):
    elastic: ElasticSettings
    postgres_movies: PostgresSettings

    class Config:
        env_file = (
            os.path.join(ENV_DIR, ".env"),
            os.path.join(ENV_DIR, ".env.dev"),
        )
        env_nested_delimiter = "__"


settings = Settings()
