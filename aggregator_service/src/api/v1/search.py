import requests
from api.v1.utils import verify_token
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from core.config import ROOT_PATH
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
    try:
        # Get movie details from an external API
        movie = requests.get(
            f"http://{settings.server_host}/api/v1/movies/{film_id}"
        ).json()
    except Exception:
        # If the external API is down, return mock data to allow
        # the user to still generate a link for watching movies
        movie = {
            "title": "404",
            "rating": "404",
            "creation_date": "2004",
            "genres": ["404"],
        }

    return templates.TemplateResponse(
        "movie.html",
        {
            "request": request,
            "movie": movie,
            "omdb_key": settings.api_keys.omdb,
            "server_host": settings.server_host,
        },
    )
