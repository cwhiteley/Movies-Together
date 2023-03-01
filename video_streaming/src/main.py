import json

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

movies_database = {
    1: {
        "video_file_path": "static/videos/mac_studio.mp4",
        "title": "Mac studio",
        "poster_file_path": "images/mac_studio.jpg",
    },
    2: {"video_file_path": 'static/videos/pixel_6.mp4',
        "title": "Pixel 6",
        "poster_file_path": "images/pixel_6.jpg", }
}

sessions = {
    123: set(),
    456: set()
}

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/{movie_id}")
async def index(request: Request, movie_id: int, session_id: int
                ):
    movie = await find_movie_by_id(movie_id)
    context = {
        "request": request,
        "movie_id": movie_id,
        "movie_title": movie["title"],
        "movie_poster": movie["poster_file_path"],
        "session_id": session_id
    }

    return templates.TemplateResponse("index.html", context)


async def find_movie_by_id(movie_id: int):
    return movies_database[movie_id]


@app.get("/video/{movie_id}", name="stream_video")
async def stream_video(movie_id: int):
    movie = await find_movie_by_id(movie_id)
    return FileResponse(movie["video_file_path"], media_type="video/mp4")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,
                             ):
    await websocket.accept()
    session_id = int(websocket.query_params.get('session_id'))

    current_session = sessions[session_id]
    current_session.add(websocket)

    try:
        while True:
            message = await websocket.receive_text()
            message_data = json.loads(message)

            if message_data["event_name"] == "play":
                for connection in current_session:
                    await connection.send_text(
                        json.dumps({"event_name": "play", "user": message_data["user"]})
                    )

            elif message_data["event_name"] == "pause":
                for connection in current_session:
                    await connection.send_text(
                        json.dumps(
                            {"event_name": "pause", "user": message_data["user"]}
                        )
                    )

            elif message_data["event_name"] == "change_time":
                for connection in current_session:
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
        current_session.remove(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
