import json

import fastapi
from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from services.groups import GroupsService, get_groups_service

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.post(
    "/{film_id}",
    summary="Create a group movie channel.",
    description="Create a group movie channel and generate a link to yourself.",
    response_description="Return link to stream.",
)
async def path(
    film_id: str, service: GroupsService = Depends(get_groups_service)
) -> str:
    link = await service.create_chat(film_id=film_id, user_id="user")
    return JSONResponse(content=jsonable_encoder(link))


@router.get(
    "/view/{link_id}",
    summary="Connect to group view.",
    description="Connect to server socket.",
    response_description="Return status.",
)
async def path(
    link_id: str, request: Request, service: GroupsService = Depends(get_groups_service)
) -> str:
    data = await service.get_data_from_cache(link_id)
    film_id = data.get("film_id")
    if not film_id:
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder({"message": "group view not found"}),
        )
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "host": "localhost",
            "host_chat": "localhost",
            "port_chat": "8001",
            "port": "8000",
            "path_video_socket": f"/api/v1/groups/ws/video/{link_id}",
            "path_chat_socket": f"/api/v1/groups/ws/chat/{link_id}",
            "film_id": f"{film_id}",
        },
    )


clients = []
active_connections = set()


@router.websocket("/ws/video/{link_id}")
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


# @router.websocket("/ws/chat/{link_id}")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     active_connections.add(websocket)
#     try:
#         while True:
#             data = await websocket.receive_text()
#             message = json.loads(data)
#             for connection in active_connections:
#                 await connection.send_text(f"User_{message['user']}: {message['data']}")
#     except WebSocketDisconnect:
#         active_connections.remove(websocket)
