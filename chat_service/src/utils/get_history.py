import json

from fastapi import WebSocket
from redis.asyncio import Redis

from models.chat import Chat, Message


async def get_history(redis_conn: Redis, websocket: WebSocket, chat: Chat):
    history = await redis_conn.get(chat.id)
    if history:
        chat.messages = json.loads(history)
        for message in chat.messages:
            message = Message(**message)
            await websocket.send_text(
                f"{message.timestamp}: User_{message.user}: {message.data}"
            )
