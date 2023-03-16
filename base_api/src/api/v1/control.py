from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from services.groups import GroupsService, get_groups_service
from utils.user import get_user
import json

router = APIRouter()


active_connections = set()


@router.websocket("/ws/{link_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    link_id: str,
    service: GroupsService = Depends(get_groups_service),
):
    cache_data = await service.get_data_from_cache(link_id)
    user = await get_user(cokies=websocket.cookies)

    if user not in cache_data["black_list"]:
        await websocket.accept()
        active_connections.add(websocket)

        cache_data["clients"].append({user: websocket.client})
        await service.set_data_to_cache(key=link_id, data=cache_data)
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                if message.get("command") == "Delete user" and message.get(
                    "user_name"
                ) != cache_data.get("user"):
                    await service.ban_user(key=link_id, user_name=message["user_name"])
                    current_host, current_port = [
                        client.get(message["user_name"])
                        for client in cache_data["clients"]
                        if client.get(message["user_name"])
                    ][0]
                    if current_host and current_port:
                        for connection in active_connections:
                            if current_host == connection.client.__getattribute__(
                                "host"
                            ) and current_port == connection.client.__getattribute__(
                                "port"
                            ):
                                await connection.send_text(f"closed connection")
                                current_host, current_port = None, None
                            await connection.send_text(
                                f"user {message['user_name']} has been removed from the channel"
                            )
        except WebSocketDisconnect:
            active_connections.remove(websocket)
