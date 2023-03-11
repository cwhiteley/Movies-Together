import json
import logging

import uvicorn
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

active_connections = set()
paused = False
current_time = 0
loop = asyncio.get_event_loop()
send_current_time = None


@app.websocket("/api/v1/groups/ws/video/{link_id}")
async def websocket_endpoint(websocket: WebSocket, link_id: str):
    await websocket.accept()
    active_connections.add(websocket)
    global paused, current_time, send_current_time

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message['event_name'] == 'play':
                paused = False
                current_time = message['time']
                for connection in active_connections:
                    await connection.send_text(json.dumps({'event_name': 'play', 'time': current_time}))

                if send_current_time is None:
                    send_current_time = loop.create_task(send_time())

            elif message['event_name'] == 'pause':
                paused = True
                print(paused)
                current_time = message['time']
                for connection in active_connections:
                    await connection.send_text(json.dumps({'event_name': 'pause', 'time': current_time}))

            elif message['event_name'] == 'change_time':
                current_time = message['time']
                for connection in active_connections:
                    await connection.send_text(json.dumps({'event_name': 'change_time', 'time': current_time}))

            elif message['event_name'] == 'connect':
                for connection in active_connections:
                    await connection.send_text(
                        json.dumps({'event_name': 'change_time', 'time': current_time, 'paused': paused}))

    except WebSocketDisconnect:
        active_connections.remove(websocket)

        if len(active_connections) == 0 and send_current_time is not None:
            send_current_time.cancel()
            send_current_time = None


async def send_time():
    global paused, current_time

    while True:
        await asyncio.sleep(1)
        if not paused:

            current_time += 1
            for connection in active_connections:
                await connection.send_text(
                    json.dumps({'event_name': 'change_time', 'time': current_time, 'user': 'server'}))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.chat_service.host,
        # port=settings.chat_service.port,
        port=8002,
        reload=True,
    )
