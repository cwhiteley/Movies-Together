from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


@router.get(
    "/{film_id}",
    summary="Connect to group view.",
    description="Connect to server socket.",
    response_description="Return status.",
)
async def stream_video(film_id: str):
    # TODO сделать получение расположения фильма из базы
    video_file_path = f"static/videos/{film_id}.mp4"
    # video_file_path = f"./src/static/videos/{film_id}.mp4"
    return FileResponse(video_file_path, media_type="video/mp4")
