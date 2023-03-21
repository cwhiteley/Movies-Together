from api.tools import validate_not_found
from api.v1.schemes import FullFilm, ShortFilm
from db.redis import redis_cache
from fastapi import APIRouter, Depends, Query, Request
from services.film import FilmService, get_film_service

FILM_CACHE_EXPIRE_IN_SECONDS = 60

router = APIRouter()


@router.get(
    "", response_model=list[ShortFilm], summary="Filter by genre and sort by rating"
)
@redis_cache(ShortFilm, expired=FILM_CACHE_EXPIRE_IN_SECONDS)
async def get_many(
    request: Request,
    service: FilmService = Depends(get_film_service),
    page_num: int = 1,
    page_size: int = 50,
    sort_by: str = Query(
        default="-imdb_rating",
        regex="^-?imdb_rating",
        alias="sort",
        description="Sort by rating",
    ),
    filter_film_by_genre_id: str = Query(default=None, alias="filter[genre]"),
) -> list[ShortFilm]:
    """Movie filter by genre and sort by rating"""
    objs = await service.search(
        page_num=page_num,
        page_size=page_size,
        sort_by=sort_by,
        filter_film_by_genre_id=filter_film_by_genre_id,
    )

    validate_not_found(objs, "film_not_found")
    return [ShortFilm(**x.dict()) for x in objs]


@router.get("/search", response_model=list[ShortFilm], summary="Movie search")
@redis_cache(ShortFilm, expired=FILM_CACHE_EXPIRE_IN_SECONDS)
async def search(
    request: Request,
    service: FilmService = Depends(get_film_service),
    page_num: int = 1,
    page_size: int = 50,
    query: str | None = Query(default=None, description="Movie name"),
) -> list[ShortFilm]:
    """Movie search"""

    objs = await service.search(page_num=page_num, page_size=page_size, query=query)
    validate_not_found(objs, "film_not_found")
    return [ShortFilm(**x.dict()) for x in objs]


@router.get("/{film_id}", response_model=FullFilm, summary="Detail movie information")
@redis_cache(FullFilm, expired=FILM_CACHE_EXPIRE_IN_SECONDS)
async def details(
    request: Request, film_id: str, service: FilmService = Depends(get_film_service)
) -> FullFilm:
    """Get detail movie information"""
    obj = await service.get_by_id(film_id)
    validate_not_found(obj, "film_not_found")
    return FullFilm(**obj.dict())
