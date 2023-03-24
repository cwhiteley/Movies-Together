import asyncio
import json
from collections import defaultdict

from db.cache import get_redis_client, RedisClient
from fastapi import APIRouter
from fastapi import WebSocket, WebSocketDisconnect, Depends
from models.video_context import VideoContext
from utils.user import get_user_and_token

router = APIRouter()

loop = asyncio.get_event_loop()
video_contexts = defaultdict(VideoContext)


async def save_viewing_time(
        link_id: str,
        video_context: VideoContext,
        redis_client: RedisClient
):
    while True:
        await asyncio.sleep(10)
        print(f"Saving time: {video_context.current_time}")
        await redis_client.set(
            f"viewing_time:{link_id}", {"sec": video_context.current_time}, expire=60
        )


async def get_viewing_time(redis_client: RedisClient, link_id: str):
    viewing_time = await redis_client.get(link_id)
    print('Getting time ', viewing_time)
    if viewing_time is None:
        return 0
    return viewing_time["sec"]


async def send_time(video_context: VideoContext):
    while True:
        await asyncio.sleep(1)
        if not video_context.paused:
            print(video_context.paused)
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


@router.websocket("/api/v1/groups/ws/video/{link_id}")
async def video_control_websocket(
        websocket: WebSocket,
        link_id: str,
        redis_client: RedisClient = Depends(get_redis_client),
):
    cache_data = await redis_client.get(link_id)
    user, view_token = get_user_and_token(params=websocket.query_params, link=link_id)

    # Check if the user is in the blacklist and deny access if they are
    if view_token not in cache_data["black_list"] and not websocket.query_params.get(link_id):
        await websocket.accept()
        video_context = video_contexts[link_id]
        video_context.active_connections.add(websocket)
        print(video_context)

        # If this is the first connection for the VideoContext, retrieve
        # the current viewing time from Redis and assign it to the VideoContext object
        if len(video_context.active_connections) == 1:
            video_context.current_time = await get_viewing_time(redis_client, f"viewing_time:{link_id}")
            print(f"Current time: {video_context.current_time}")

        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)

                if message["event_name"] == "play":
                    video_context.paused = False
                    for connection in video_context.active_connections:
                        await connection.send_text(
                            json.dumps(
                                {"event_name": "play", "time": video_context.current_time}
                            )
                        )

                    if video_context.send_current_time is None:
                        print('Creating task 1')

                        video_context.send_current_time = loop.create_task(
                            send_time(video_context)
                        )
                    if video_context.save_current_time is None:
                        print('Creating task 2')
                        video_context.save_current_time = loop.create_task(
                            save_viewing_time(link_id, video_context, redis_client)
                        )
                    print('Task created')
                elif message["event_name"] == "pause":
                    video_context.paused = True
                    video_context.current_time = message["time"]
                    for connection in video_context.active_connections:
                        await connection.send_text(
                            json.dumps(
                                {"event_name": "pause", "time": video_context.current_time}
                            )
                        )

                elif message["event_name"] == "change_time":
                    video_context.current_time = message["time"]
                    for connection in video_context.active_connections:
                        await connection.send_text(
                            json.dumps(
                                {
                                    "event_name": "change_time",
                                    "time": video_context.current_time,
                                }
                            )
                        )

                elif message["event_name"] == "connect":
                    for connection in video_context.active_connections:
                        await connection.send_text(
                            json.dumps(
                                {
                                    "event_name": "change_time",
                                    "time": video_context.current_time,
                                    "paused": video_context.paused,
                                }
                            )
                        )

        except WebSocketDisconnect:
            video_context.active_connections.remove(websocket)

            if (
                    len(video_context.active_connections) == 0
                    and video_context.send_current_time is not None
            ):
                video_context.send_current_time.cancel()
                video_context.send_current_time = None
            if (
                    len(video_context.active_connections) == 0
                    and video_context.save_current_time is not None
            ):
                video_context.save_current_time.cancel()
                video_context.save_current_time = None
