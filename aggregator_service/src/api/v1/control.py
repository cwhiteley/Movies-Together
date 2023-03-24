import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from services.groups import GroupsService, get_groups_service
from utils.user import get_user_and_token

router = APIRouter()


active_connections = set()


@router.websocket("/ws/{link_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    link_id: str,
    service: GroupsService = Depends(get_groups_service),
):
    cache_data = await service.get_data_from_cache(link_id)

    user, view_token = get_user_and_token(params=websocket.query_params, link=link_id)

    # Check if the user is in the blacklist and deny access if they are
    if view_token not in cache_data["black_list"] and not websocket.query_params.get(
        link_id
    ):
        websocket.cookies[link_id] = view_token
        await websocket.accept()
        active_connections.add(websocket)

        # Add a token for the current channel
        await websocket.send_json(
            data={
                "token_value": view_token,
                "token_key": link_id,
                "message": f" User: {user} connected",
            }
        )

        # Add the user to the cache, for further comparison
        cache_data["clients"].append({user: str(websocket.cookies.get(link_id))})
        await service.set_data_to_cache(key=link_id, data=cache_data)
        try:
            while True:
                # Refresh data from cache
                cache_data = await service.get_data_from_cache(link_id)
                data = await websocket.receive_text()
                message = json.loads(data)
                # Checking that user data exists
                client = [
                    client
                    for client in cache_data["clients"]
                    if client.get(message.get("user_name"))
                ]
                if (
                    message.get("command") == "Delete user"
                    and message.get("user_name") != cache_data.get("user")
                    and client
                ):
                    await service.ban_user(
                        key=link_id, token=client[0].get(message.get("user_name"))
                    )
                else:
                    continue

                for connection in active_connections:
                    # Recognize session by token and execute commands
                    if connection.cookies.get(link_id) in client[0].get(
                        message.get("user_name")
                    ):
                        await connection.send_json(
                            data={
                                "command": message.get("command"),
                                "message": f"user {message['user_name']} has been removed from the channel",
                            }
                        )
        except WebSocketDisconnect:
            active_connections.remove(websocket)
