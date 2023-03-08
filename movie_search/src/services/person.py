from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from core.config import settings
from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from services.base import BaseService


class PersonService(BaseService):
    model_cls = Person
    es_index = settings.elastic.index.person
    query_param = "full_name"


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
