from functools import lru_cache
from json import dumps
from db.redis import Redis, get_cache_conn
from fastapi import Depends
from aioredis import Redis as aio_redis


class GroupsService(Redis):
    def __init__(self, redis_conn: aio_redis):
        super().__init__(redis_conn)

    async def create_chat(self, film_id: str, user_id: str):
        link_key = await self.create_key([film_id, user_id])
        # TODO create socket server for chat
        # add information for connection to redis
        await self.set_cache(key=link_key, data=dumps({'info': 'data'}))
        return link_key




# @lru_cache()
async def get_groups_service(redis_conn: aio_redis = Depends(get_cache_conn)):
    return GroupsService(redis_conn)