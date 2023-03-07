from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from core.config import settings
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film
from services.base import BaseService


class FilmService(BaseService):
    model_cls = Film
    es_index = settings.elastic.index.filmwork
    query_param = "title"


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
