from __future__ import annotations

from elasticsearch import AsyncElasticsearch

es: AsyncElasticsearch | None = None


# Функция понадобится при внедрении зависимостей
async def get_elastic() -> AsyncElasticsearch:
    return es


class Query:
    """Class query tree structure in elastic"""

    def __init__(self, query: str, value: dict | list) -> None:
        if query not in ["term", "terms", "match"]:
            raise ValueError["Wrong query"]
        self._query = {query: value}

    def dict(self) -> dict:
        return self._query


class QueryTree:
    """Class for making query tree structure in elastic"""

    def __init__(self) -> None:
        self._query = {}
        self._conditions = {
            "must": [],
            "should": [],
            "filter": [],
        }

    def dict(self) -> dict:
        """Create dict query object"""
        if self._is_empty():
            self._conditions["must"].append({"match_all": {}})
        return {"bool": {k: v for k, v in self._conditions.items() if v}}

    def add(self, obj: Query | QueryTree, condition: str = "must"):
        """Add a node or subquery"""
        self._conditions[condition].append(obj.dict())

    def add_nested(self, path: str, obj: QueryTree, condition: str = "must"):
        """Add nested subquery"""
        self._conditions[condition].append(
            {"nested": {"path": path, "query": obj.dict()}}
        )

    def _is_empty(self):
        for v in self._conditions.values():
            if v:
                return False
        return True
