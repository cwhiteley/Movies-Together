import json
import logging
from datetime import datetime
import re

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import ORJSONResponse
from utils.user import get_user
from redis import asyncio as aioredis
from pydantic.json import pydantic_encoder

from core.config import settings
from db import redis_cache
from redis.asyncio import Redis
from models.chat import Chat, Message
from utils.get_history import get_history

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="API for group chat",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

active_connections = set()
redis_conn = Redis


'''вебсокет чата: присоединяемся  к вебсокету, проверяем или создаем запись с историей чата, отправляем-принимаем сообщения чата'''
@app.websocket("/api/v1/groups/ws/chat/{link_id}")
async def chat_endpoint(websocket: WebSocket):
    redis_conn = await aioredis.Redis(
        host=settings.redis.host, port=settings.redis.port, decode_responses=True
    )
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
