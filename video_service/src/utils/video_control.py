from models.video_context import VideoContext
from db.cache import RedisClient
import asyncio
import json


async def save_viewing_time(
    link_id: str, video_context: VideoContext, redis_client: RedisClient
):
    while True:
        await asyncio.sleep(10)
        await redis_client.set(
            f"viewing_time:{link_id}", {"sec": video_context.current_time}, expire=60
        )


async def get_viewing_time(redis_client: RedisClient, link_id: str):
    viewing_time = await redis_client.get(f"viewing_time:{link_id}")
    if viewing_time is None:
        return 0
    return viewing_time["sec"]


async def send_time(video_context: VideoContext):
    while True:
        await asyncio.sleep(1)
        if not video_context.paused:
            video_context.current_time += 1
            for connection in video_context.active_connections:
                await connection.send_text(
                    json.dumps(
                        {
                            "event_name": "change_time",
                            "time": video_context.current_time,
                            "user": "server",
                        }
                    )
                )
