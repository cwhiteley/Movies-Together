import json
import logging

import uvicorn
from core.config import settings
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import ORJSONResponse

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="API for group video",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

active_connections = set()


@app.websocket("/api/v1/groups/ws/video/{link_id}")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            message_data = json.loads(message)

            if message_data["event_name"] == "play":
                for connection in active_connections:
                    await connection.send_text(
                        json.dumps({"event_name": "play", "user": message_data["user"]})
                    )

            elif message_data["event_name"] == "pause":
                for connection in active_connections:
                    await connection.send_text(
                        json.dumps(
                            {"event_name": "pause", "user": message_data["user"]}
                        )
                    )

            elif message_data["event_name"] == "change_time":
                for connection in active_connections:
                    await connection.send_text(
                        json.dumps(
                            {
                                "event_name": "change_time",
                                "time": message_data["time"],
                                "user": message_data["user"],
                            }
                        )
                    )
    except WebSocketDisconnect:
        active_connections.remove(websocket)



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.chat_service.host,
        port=settings.chat_service.port,
        reload=True,
    )
