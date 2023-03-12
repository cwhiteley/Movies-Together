from fastapi import APIRouter, Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from services.groups import GroupsService, get_groups_service
from core.config import settings
from starlette.responses import JSONResponse

# from starlette.responses import JSONResponse

router = APIRouter()

templates = Jinja2Templates(directory="templates")
# templates = Jinja2Templates(directory="./src/templates")


@router.post(
    "/{film_id}",
    summary="Create a group movie channel.",
    description="Create a group movie channel and generate a link to yourself.",
    response_description="Return link to stream.",
)
async def path(
    film_id: str, service: GroupsService = Depends(get_groups_service)
) -> JSONResponse:
    link = await service.create_chat(film_id=film_id, user_id="user")
    return JSONResponse(content={"link": link}, status_code=200)


@router.get(
    "/view/{link_id}",
    summary="Connect to group view.",
    description="Connect to server socket.",
    response_description="Return status.",
)
async def path(
    link_id: str, request: Request, service: GroupsService = Depends(get_groups_service)
):
    data = await service.get_data_from_cache(link_id)
    film_id = data.get("film_id")
    if not film_id:
        return JSONResponse(
            status_code=500,
            content={"message": "group view not found"},
        )
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user_owner": data.get("user_id"),
            "video_host": settings.video_service.host,
            "video_port": settings.video_service.port,
            "chat_host": settings.chat_service.host,
            "chat_port": settings.chat_service.port,
            "path_video_socket": f"/api/v1/groups/ws/video/{link_id}",
            "path_chat_socket": f"/api/v1/groups/ws/chat/{link_id}",
            "film_id": f"{film_id}",
            "server_host": settings.server_host,
        },
    )
