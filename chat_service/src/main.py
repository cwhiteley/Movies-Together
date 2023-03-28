import json
import logging
import re
from datetime import datetime

import backoff
import redis as redis_bibl
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import ORJSONResponse
from pydantic.json import pydantic_encoder
from redis import asyncio as aioredis

from core.config import settings
from db import redis_cache
from models.chat import Chat, Message
from utils.get_history import get_history
from utils.user import get_user_and_token

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="API for group chat",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

active_connections = set()


@app.websocket("/api/v1/groups/ws/chat/{link_id}")
async def chat_endpoint(websocket: WebSocket, link_id: str):
    """
    WebSocket endpoint for chat functionality.

    Connects to the WebSocket, checks if a chat history record exists for the provided link ID,
    and creates one if it doesn't. Enables sending and receiving chat messages via the WebSocket.

    Args:
        websocket (WebSocket): An instance of the WebSocket class provided by FastAPI.
        link_id (str): The ID of the chat history record to be accessed or created.
    """

    redis_conn = await aioredis.Redis(
        host=settings.redis.host, port=settings.redis.port, decode_responses=True
    )

    cache_not_parse = await redis_conn.get(link_id)
    cache_data = json.loads(cache_not_parse)
    user, view_token = get_user_and_token(params=websocket.query_params, link=link_id)

    # Check if the user is in the blacklist and deny access if they are
    if view_token not in cache_data["black_list"] and not websocket.query_params.get(
        link_id
    ):
        await websocket.accept()
        active_connections.add(websocket)

        # Create chat id from websocket link
        link_id = re.search(r"chat\/([\w-]+)", websocket.url.path).group(1)
        chat = Chat(id=f"chat{link_id}")
        # Get chat history, if there is a history, send history to joined user"""
        await get_history(redis_conn=redis_conn, websocket=websocket, chat=chat)

        try:
            while True:
                data = await websocket.receive_json()
                message = Message(**data)
                message.timestamp = datetime.now().time().replace(microsecond=0)
                for connection in active_connections:
                    await connection.send_text(
                        f"{message.timestamp}: User_{message.user}: {message.data}"
                    )
                    # Update and record chat history into cache storage (redis)
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
