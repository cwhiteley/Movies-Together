from core.config import ROOT_PATH
import requests
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from api.v1.utils import verify_token
from core.config import settings

router = APIRouter()

if settings.debug:
    templates = Jinja2Templates(directory=f"templates")
else:
    templates = Jinja2Templates(directory=f"{ROOT_PATH}templates")


@router.get(
    "/",
    summary="Connect to group view.",
    description="Connect to server socket.",
    response_description="Return status.",
    name="Search",
)
async def search_movie(request: Request, payload=Depends(verify_token)):
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
