from fastapi import APIRouter, Depends
from services.groups import get_groups_service, GroupsService

router = APIRouter()


@router.post(
    "/{film_id}",
    summary="Create a group movie channel.",
    description="Create a group movie channel and generate a link to yourself.",
    response_description="Return link to stream.",
)
async def path(
        film_id: str,
        service: GroupsService = Depends(get_groups_service)
    ) -> str:
    link = await service.create_chat(film_id=film_id, user_id='user')
    return link


@router.post(
    "/view/{link_id}",
    summary="Connect to group view.",
    description="Connect to server socket.",
    response_description="Return status.",
)
async def path(
        link_id: str,
    ) -> str:
    return 'status'