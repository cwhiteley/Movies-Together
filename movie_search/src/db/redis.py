import functools

from aioredis import Redis
from fastapi import Request
from pydantic import BaseModel, parse_raw_as
from pydantic.error_wrappers import ValidationError

redis: Redis | None = None


# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    return redis


def redis_cache(model_cls, expired: int = 50):
    """Cache decorator"""

    def wraps(fn):
        @functools.wraps(fn)
        async def decorated(request: Request, **kwargs):
            key = request.url.path + "?" + str(request.query_params)
            data = await _from_redis_cache(model_cls, key)

            if data:
                return data

            data = await fn(request, **kwargs)

            if data is None:
                return None

            await _to_redis_cache(key, data, expire_time=expired)
            return data

        return decorated

    return wraps


async def _from_redis_cache(model_cls, key: str):
    """Get data from redis"""
    data = await redis.get(key)
    if not data:
        return None

    try:
        return parse_raw_as(list[model_cls], data)
    except ValidationError:
        return model_cls.parse_raw(data)


async def _to_redis_cache(
    key: str, data: BaseModel | list[BaseModel], expire_time: int
):
    """Save data to redis"""
    if type(data) is list:
        serialized_objs = [x.json() for x in data]
        serialized_str = ",".join(serialized_objs)
        json_data = f"[{serialized_str}]"
    else:
        json_data = data.json()

    await redis.set(key, json_data, expire=expire_time)
