import json
import logging
from datetime import datetime
import re

import backoff
import redis as redis_bibl
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import ORJSONResponse
from utils.user import get_user_and_token
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


'''вебсокет чата: присоединяемся  к вебсокету, проверяем или создаем запись с историей чата, отправляем-принимаем сообщения чата'''
@app.websocket("/api/v1/groups/ws/chat/{link_id}")
async def chat_endpoint(websocket: WebSocket, link_id: str):
    redis_conn = await aioredis.Redis(
        host=settings.redis.host, port=settings.redis.port, decode_responses=True
    )

    cache_not_parse = await redis_conn.get(link_id)
    cache_data = json.loads(cache_not_parse)
    user, view_token = get_user_and_token(params=websocket.query_params, link=link_id)

    # если пользователь есть в black_list, то не пускаю
    if view_token not in cache_data["black_list"] and not websocket.query_params.get(link_id):
        await websocket.accept()
        active_connections.add(websocket)

        # create chat id from websocket link
        link_id = re.search(r"chat\/([\w-]+)", websocket.url.path).group(1)
        chat = Chat(id=f"chat{link_id}")
        # get chat history, if there is a history, send history to joined user"""
        await get_history(redis_conn=redis_conn, websocket=websocket, chat=chat)

        try:
            while True:
                data = await websocket.receive_json()
                message = Message(**data)
                message.timestamp = datetime.now().time().replace(microsecond=0)
                for connection in active_connections:
                    await connection.send_text(f"{message.timestamp}: User_{message.user}: {message.data}")
                    # update and record chat history into cache storage (redis)
                    chat.messages.append(message)
                    history = chat.messages
                    history = json.dumps(history, default=pydantic_encoder)
                    await redis_conn.set(chat.id, history)
        except WebSocketDisconnect:
            active_connections.remove(websocket)
        if redis_cache.redis_conn is not None:
            await redis_cache.redis_conn.close()
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

