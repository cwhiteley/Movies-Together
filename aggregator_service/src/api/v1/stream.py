from fastapi import APIRouter
from fastapi.responses import FileResponse

from core.config import ROOT_PATH

router = APIRouter()


@router.get(
    "/{film_id}",
    summary="Connect to group view.",
    description="Connect to server socket.",
    response_description="Return status.",
)
async def stream_video(film_id: str):
    # TODO сделать получение расположения фильма из базы
    video_file_path = f"{ROOT_PATH}static/videos/{film_id}.mp4"
    return FileResponse(video_file_path, media_type="video/mp4")
