from typing import Optional

# from aioredis import Redis
from redis.asyncio import Redis

# переменная хранит объект подключения после чего передачи
redis_conn: Optional[Redis] = None


async def get_cache_conn() -> Optional[Redis]:
    """Вернуть подключение к redis, если оно создано, иначе None."""
    return redis_conn


class Redis:
    """Реализация интерфейса кэша и работающая через redis."""

    def __init__(self, redis_conn: Redis):
        self.redis: Redis = redis_conn
