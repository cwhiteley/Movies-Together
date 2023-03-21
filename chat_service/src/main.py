import json
import logging
from datetime import datetime
import re

import backoff
import redis as redis_bibl
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import ORJSONResponse
from redis import asyncio as aioredis
from pydantic.json import pydantic_encoder

from core.config import settings
from models.chat import Chat, Message
from utils.get_history import get_history
from db import redis_cache
from db.redis_cache import get_cache_conn, Redis

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="API for group chat",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

active_connections = set()


@app.on_event("startup")
@backoff.on_exception(
    backoff.expo,
    (redis_bibl.exceptions.ConnectionError),
    max_time=1000,
    max_tries=10,
)
async def startup():
    redis_cache.redis_conn = await aioredis.Redis(
        host=settings.redis.host, port=settings.redis.port, decode_responses=True
    )
    await redis_cache.redis_conn.ping()

    logging.info("Create connections")


@app.websocket("/api/v1/groups/ws/chat/{link_id}")
async def chat_endpoint(websocket: WebSocket, cache: Redis = Depends(get_cache_conn)):
    """вебсокет чата: присоединяемся  к вебсокету, проверяем или создаем запись с историей чата, отправляем-принимаем сообщения чата"""
    print(cache)
    await websocket.accept()
    active_connections.add(websocket)
    link_id = re.search(r"chat\/([\w-]+)", websocket.url.path).group(1)
    chat = Chat(id=f"chat{link_id}")
    await get_history(redis_conn=cache, websocket=websocket, chat=chat)

    try:
        while True:
            data = await websocket.receive_json()
            message = Message(**data)
            message.timestamp = datetime.now().time().replace(microsecond=0)
            for connection in active_connections:
                await connection.send_text(f"{message.timestamp}: User_{message.user}: {message.data}")
            chat.messages.append(message)
            history = chat.messages
            history = json.dumps(history, default=pydantic_encoder)
            await cache.set(chat.id, history)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
    if cache is not None:
        await cache.close()
