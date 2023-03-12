from functools import lru_cache
from json import dumps, loads

# from aioredis import Redis as aio_redis
from redis.asyncio import Redis as aio_redis
from db.redis_cache import Redis, get_cache_conn
from fastapi import Depends


class GroupsService(Redis):
    def __init__(self, redis_conn: aio_redis):
        super().__init__(redis_conn)

    async def create_chat(self, film_id: str, user_id: str):
        link_key = await self.create_key([film_id, user_id])
        # TODO create socket server for chat
        # add information for connection to redis
        await self.set_cache(
            key=link_key, data=dumps({"film_id": film_id, "user_id": user_id, "clients": [user_id]})
        )
        return link_key

    async def get_data_from_cache(self, key: str):
        data = await self.get_cache(key=key)
        return loads(data)


# @lru_cache()
async def get_groups_service(redis_conn: aio_redis = Depends(get_cache_conn)):
    return GroupsService(redis_conn)
