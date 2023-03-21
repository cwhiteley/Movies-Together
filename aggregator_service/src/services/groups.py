from json import dumps, loads

from db.cache_db import Redis, get_cache_conn
from fastapi import Depends
from redis.asyncio import Redis as aio_redis


class GroupsService(Redis):
    def __init__(self, redis_conn: aio_redis):
        super().__init__(redis_conn)

    async def create_chat(self, film_id: str, user_id: str):
        link_key = await self.create_key([film_id, user_id])
        await self.set_cache(
            key=link_key,
            data=dumps(
                {"film_id": film_id, "user": user_id, "clients": [], "black_list": []}
            ),
        )
        return link_key

    async def get_data_from_cache(self, key: str):
        data = await self.get_cache(key=key)
        return loads(data)

    async def set_data_to_cache(self, key: str, data: dict):
        await self.set_cache(key=key, data=dumps(data))

    async def ban_user(self, key: str, token: str):
        data = await self.get_data_from_cache(key=key)
        data["black_list"].append(token)
        await self.set_cache(key=key, data=dumps(data))
        return True


async def get_groups_service(redis_conn: aio_redis = Depends(get_cache_conn)):
    return GroupsService(redis_conn)
