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

    user, view_token = get_user_and_token(cokies=websocket.cookies, link=link_id)

    # если пользователь есть в black_list, то не пускаю
    if view_token not in cache_data["black_list"] and not websocket.cookies.get(link_id):
        await websocket.accept()
        active_connections.add(websocket)

        # добавляю токен для текущего каначала
        await websocket.send_json(data={"token_value": view_token,
                                        "token_key": link_id,
                                        "message": f" User: {user} connected"
                                        })

        # добавляю пользователя в кеш, для дальнейшего сравнения
        cache_data["clients"].append({user: str(websocket.cookies.get(link_id))})
        await service.set_data_to_cache(key=link_id, data=cache_data)
        try:
            while True:
                # обновляю данные из кеша
                cache_data = await service.get_data_from_cache(link_id)
                data = await websocket.receive_text()
                message = json.loads(data)
                # проверка, что данные пользователь существует
                client = [client for client in cache_data["clients"] if client.get(message.get("user_name"))]
                if message.get("command") == "Delete user" and message.get(
                    "user_name"
                ) != cache_data.get("user") and client:
                    await service.ban_user(key=link_id, token=client[0].get(message.get("user_name")))
                else:
                    continue

                for connection in active_connections:
                    # узнаю сессию по токену, и выполняю команды
                    if connection.cookies.get(link_id) in client[0].get(message.get("user_name")):
                        await connection.send_json(data={"command": message.get("command"),
                                                         "message": f"user {message['user_name']} has been removed from the channel"})
        except WebSocketDisconnect:
            active_connections.remove(websocket)
