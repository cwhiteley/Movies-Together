from abc import ABC

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from models.base import CinemaModel
from services.tools import make_elastic_params, not_found_error


class BaseService(ABC):
    model_cls = CinemaModel
    es_index = ""
    query_param = ""

    """Base class service"""

    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, id: str) -> CinemaModel | None:
        """Get movie by id"""
        return await self._get_by_id_from_elastic(id) or None

    async def search(self, **kwargs) -> list[CinemaModel] | None:
        return await self._search_from_elastic(**kwargs) or None

    @not_found_error
    async def _get_by_id_from_elastic(self, id: str) -> CinemaModel | None:
        """Get movie by id from elastic"""
        doc = await self.elastic.get(self.es_index, id)
        return self.model_cls(**doc["_source"])

    @not_found_error
    async def _search_from_elastic(self, **kwargs) -> list[CinemaModel]:
        """Searching mobies in elastic"""
        params = make_elastic_params(self.query_param, **kwargs)

        docs = await self.elastic.search(**params)

        return [self.model_cls(**doc["_source"]) for doc in docs["hits"]["hits"]]
