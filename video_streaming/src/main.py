import json

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

clients = []
active_connections = set()
video_file_path = "static/videos/Video.mp4"

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/video")
async def stream_video():
    return FileResponse(video_file_path, media_type="video/mp4")


@app.websocket("/ws")
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
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
