from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from services.groups import GroupsService, get_groups_service
from utils.user import get_user
import json

router = APIRouter()


active_connections = set()


@router.websocket("/ws/{link_id}")
async def websocket_endpoint(websocket: WebSocket,
                             link_id: str,
                             service: GroupsService = Depends(get_groups_service)):
    data = await service.get_data_from_cache(link_id)
    user = await get_user(cokies=websocket.cookies)
    # TODO Убрать not!!!!
    if not data.get("user") == user:
        await websocket.accept()
        active_connections.add(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                if message["command"] == "Delete user":
                    await service.ban_user(key=link_id, user_name=message["user_name"])
                    for connection in active_connections:
                        await connection.send_text(f"user {message['user_name']} has been removed from the channel")
        except WebSocketDisconnect:
            active_connections.remove(websocket)