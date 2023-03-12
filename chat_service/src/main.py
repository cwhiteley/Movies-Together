import json
import logging

import uvicorn
from core.config import settings
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import ORJSONResponse
from utils.user import get_user

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
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user = await get_user(cokies=websocket.cookies)
    active_connections.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            for connection in active_connections:
                await connection.send_text(f"{user}: {message['data']}")
    except WebSocketDisconnect:
        active_connections.remove(websocket)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.chat_service.host,
        port=settings.chat_service.port,
        reload=True,
    )
