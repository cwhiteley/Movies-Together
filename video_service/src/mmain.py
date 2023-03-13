import json
import logging

import uvicorn
from redis import asyncio as aioredis
from db import redis_cache
from db.redis_cache import get_cache_conn as get_redis
from core.config import settings
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import ORJSONResponse
import asyncio

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="API for group video",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)
loop = asyncio.get_event_loop()


async def startup():
    redis_cache.redis_conn = await aioredis.Redis(
        host=settings.redis.host, port=settings.redis.port, decode_responses=True
    )
    await redis_cache.redis_conn.ping()

    logging.info("Create connections")


@app.on_event("shutdown")
async def shutdown():
    if redis_cache.redis_conn is not None:
        await redis_cache.redis_conn.close()
    logging.info("Closed connections")


class VideoContext:
    def __init__(self):
        self.active_connections = set()
        self.paused = False
        self.current_time = 0
        self.send_current_time = None


async def get_video_context(link_id):
    redis = redis_cache.redis_conn
    data = await redis.get(link_id)
    if data is None:
        video_context = VideoContext()
    else:
        video_context_dict = json.loads(data)
        video_context = VideoContext()
        video_context.__dict__ = video_context_dict

    return video_context


@app.websocket("/api/v1/groups/ws/video/{link_id}")
async def websocket_endpoint(websocket: WebSocket, link_id: str):
    await websocket.accept()

    # получаем объект VideoContext для данной ссылки
    video_context = await get_video_context(link_id)

    video_context.active_connections.add(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message['event_name'] == 'play':
                video_context.paused = False
                video_context.current_time = message['time']
                for connection in video_context.active_connections:
                    await connection.send_text(json.dumps({'event_name': 'play', 'time': video_context.current_time}))

                if video_context.send_current_time is None:
                    video_context.send_current_time = loop.create_task(send_time(link_id))

            elif message['event_name'] == 'pause':
                video_context.paused = True
                video_context.current_time = message['time']
                for connection in video_context.active_connections:
                    await connection.send_text(json.dumps({'event_name': 'pause', 'time': video_context.current_time}))

            elif message['event_name'] == 'change_time':
                video_context.current_time = message['time']
                for connection in video_context.active_connections:
                    await connection.send_text(
                        json.dumps({'event_name': 'change_time', 'time': video_context.current_time}))

            elif message['event_name'] == 'connect':
                for connection in video_context.active_connections:
                    await connection.send_text(
                        json.dumps({'event_name': 'change_time', 'time': video_context.current_time,
                                    'paused': video_context.paused}))

    except WebSocketDisconnect:
        video_context.active_connections.remove(websocket)

        # сохраняем состояние видео в Redis, если в группе нет подключений
        if len(video_context.active_connections) == 0:
            redis = await get_redis()
            await redis.set(link_id, json.dumps(video_context.__dict__))

            if video_context.send_current_time is not None:
                video_context.send_current_time.cancel()
                video_context.send_current_time = None


async def send_time(link_id):
    video_context = await get_video_context(link_id)
    while True:
        await asyncio.sleep(1)
        if not video_context.paused:
            video_context.current_time += 1
            for connection in video_context.active_connections:
                await connection.send_text(
                    json.dumps({'event_name': 'change_time', 'time': video_context.current_time, 'user': 'server'}))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.video_service.host,
        # port=settings.chat_service.port,
        port=8002,
        reload=True,
    )
