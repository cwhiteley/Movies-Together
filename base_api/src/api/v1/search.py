from fastapi.responses import FileResponse
from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
import requests
from core.config import settings


router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get(
    "/",
    summary="Connect to group view.",
    description="Connect to server socket.",
    response_description="Return status.",
)
async def search_movie(request: Request):
    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "omdb_key": settings.api_keys.omdb,
            "server_host": settings.server_host,
        },
    )


@router.get("/{film_id}", summary="Get film by id")
async def movie_details(request: Request, film_id: str):
    movie = requests.get(f"http://127.0.0.1:80/api/v1/movies/{film_id}").json()
    return templates.TemplateResponse(
        "movie.html",
        {
            "request": request,
            "movie": movie,
            "omdb_key": settings.api_keys.omdb,
            "server_host": settings.server_host,
        },
    )
