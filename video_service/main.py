import asyncio
import json
import logging
from collections import defaultdict

import backoff
import redis
import uvicorn
from fastapi import FastAPI
from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import ORJSONResponse

from api.v1.control import router
from core.config import settings
from db.cache import RedisClient
from db.cache import get_redis_client
from models.video_context import VideoContext
from utils.user import get_user_and_token
from utils.video_control import save_viewing_time, get_viewing_time, send_time

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="API for group video",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)
loop = asyncio.get_event_loop()
video_contexts = defaultdict(VideoContext)


@app.on_event("startup")
@backoff.on_exception(
    backoff.expo,
    (redis.exceptions.ConnectionError),
    max_time=1000,
    max_tries=10,
)
async def startup():
    redis_client = await get_redis_client()
    redis_conn = await redis_client._get_redis()
    await redis_conn.ping()

    logging.info("Create connections")


@app.on_event("shutdown")
async def shutdown():
    redis_client = await get_redis_client()
    await redis_client.close()
    logging.info("Closed connections")


@router.websocket("/api/v1/groups/ws/video/{link_id}")
async def video_control_websocket(
    websocket: WebSocket,
    link_id: str,
    redis_client: RedisClient = Depends(get_redis_client),
):
    cache_data = await redis_client.get(link_id)
    user, view_token = get_user_and_token(params=websocket.query_params, link=link_id)

    # Check if the user is in the blacklist and deny access if they are
    if view_token not in cache_data["black_list"] and not websocket.query_params.get(
        link_id
    ):
        await websocket.accept()
        video_context = video_contexts[link_id]
        video_context.active_connections.add(websocket)
        print(video_context)

        # If this is the first connection for the VideoContext, retrieve
        # the current viewing time from Redis and assign it to the VideoContext object
        if len(video_context.active_connections) == 1:
            video_context.current_time = await get_viewing_time(
                redis_client, f"viewing_time:{link_id}"
            )
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
                                {
                                    "event_name": "play",
                                    "time": video_context.current_time,
                                }
                            )
                        )

                    if video_context.send_current_time is None:
                        print("Creating task 1")

                        video_context.send_current_time = loop.create_task(
                            send_time(video_context)
                        )
                    if video_context.save_current_time is None:
                        print("Creating task 2")
                        video_context.save_current_time = loop.create_task(
                            save_viewing_time(link_id, video_context, redis_client)
                        )
                    print("Task created")
                elif message["event_name"] == "pause":
                    video_context.paused = True
                    video_context.current_time = message["time"]
                    for connection in video_context.active_connections:
                        await connection.send_text(
                            json.dumps(
                                {
                                    "event_name": "pause",
                                    "time": video_context.current_time,
                                }
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


app.include_router(router, tags=["video"])
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.video_service.host,
        # port=settings.chat_service.port,
        port=8002,
        reload=True,
    )
