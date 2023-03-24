from api.v1.utils import verify_token
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import JSONResponse

from core.config import ROOT_PATH
from core.config import settings
from services.groups import GroupsService, get_groups_service

router = APIRouter()

templates = Jinja2Templates(directory=f"{ROOT_PATH}templates")


@router.post(
    "/{film_id}",
    summary="Create a group movie channel.",
    description="Create a group movie channel and generate a link to yourself.",
    response_description="Return link to stream.",
)
async def generate_link_id(
    film_id: str,
    service: GroupsService = Depends(get_groups_service),
    payload=Depends(verify_token),
) -> JSONResponse:
    link = await service.create_chat(film_id=film_id, user_id=payload.get("user_id"))
    return JSONResponse(content={"link": link}, status_code=200)


@router.get(
    "/view/{link_id}",
    summary="Connect to group view.",
    description="Connect to server socket.",
    response_description="Return status.",
)
async def connect_to_chanel(
    link_id: str,
    request: Request,
    service: GroupsService = Depends(get_groups_service),
    payload=Depends(verify_token),
):
    data = await service.get_data_from_cache(link_id)
    film_id = data.get("film_id")
    if not film_id:
        return JSONResponse(
            status_code=500,
            content={"message": "group view not found"},
        )
    return templates.TemplateResponse(
        "player_chat.html",
        {
            "request": request,
            "user_owner": data.get("user"),
            "control_host": settings.base_api.host,
            "control_port": settings.base_api.port,
            "video_host": settings.video_service.host,
            "video_port": settings.video_service.port,
            "chat_host": settings.chat_service.host,
            "chat_port": settings.chat_service.port,
            "path_video_socket": f"/api/v1/groups/ws/video/{link_id}",
            "path_chat_socket": f"/api/v1/groups/ws/chat/{link_id}",
            "path_control_socket": f"/api/v1/control/ws/{link_id}",
            "film_id": f"{film_id}",
            "server_host": settings.server_host,
            "username": f"{payload.get('username')}",
            "user_id": f"{payload.get('user_id')}",
            "is_owner": payload.get("user_id") == data.get("user"),
        },
    )
