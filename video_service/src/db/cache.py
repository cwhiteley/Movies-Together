import json
from typing import Optional, Any

from redis.asyncio import Redis
from redis.asyncio import ConnectionPool
from core.config import settings

import redis


class RedisClient:
    """Класс для работы с Redis."""

    def __init__(self, redis_url: str, pool_size: int = 10):
        """
        Инициализация класса.

        :param redis_url: строка подключения к Redis
        :param pool_size: размер пула соединений к Redis (по умолчанию 10)
        """
        self._redis_url = redis_url
        self._pool = ConnectionPool.from_url(self._redis_url, max_connections=pool_size)

    async def _get_redis(self) -> Redis:
        """
        Получить подключение к Redis.

        :return: подключение к Redis
        """
        return Redis(connection_pool=self._pool)

    async def close(self) -> None:
        """
        Закрыть подключение к Redis.

        :return: None
        """
        await self._pool.disconnect()

    async def get(self, key: str) -> Optional[dict[str, Any]]:
        """
        Получить данные из Redis по ключу.

        :param key: ключ для поиска данных
        :return: данные из Redis в формате словаря или None, если ключ не найден
        """
        redis = await self._get_redis()
        data = await redis.get(key)
        if data is not None:
            return json.loads(data)
        return None

    async def set(
        self, key: str, value: dict[str, Any], expire: Optional[int] = None
    ) -> None:
        """
        Сохранить данные в Redis.

        :param key: ключ для сохранения данных
        :param value: данные в формате словаря
        :param expire: время жизни ключа в секундах (по умолчанию не устанавливается)
        :return: None
        """
        redis = await self._get_redis()
        data = json.dumps(value)
        if expire is None:
            await redis.set(key, data)
        else:
            await redis.setex(key, expire, data)

    async def delete(self, key: str) -> None:
        """
        Удалить данные из Redis по ключу.

        :param key: ключ для удаления данных
        :return: None
        """
        redis = await self._get_redis()
        await redis.delete(key)

    async def exists(self, key: str) -> bool:
        """
        Проверить, существует ли ключ в Redis.

        :param key: ключ для проверки
        :return: True, если ключ существует, иначе False
        """
        redis = await self._get_redis()
        return redis.exists(key)

    async def keys(self, pattern: str) -> list:
        """
        Получить список ключей, удовлетворяющих шаблону.

        :param pattern: шаблон для поиска ключей
        :return список ключей, удовлетворяющих шаблону
        """
        redis = await self._get_redis()
        return redis.keys(pattern)


redis_client: RedisClient = RedisClient(
    redis_url=f"redis://{settings.redis.host}:{settings.redis.port}"
)


async def get_redis_client() -> RedisClient:
    return redis_client
