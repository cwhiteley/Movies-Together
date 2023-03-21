from api.tools import validate_not_found
from api.v1.schemes import Genre
from db.redis import redis_cache
from fastapi import APIRouter, Depends, Request
from services.genre import GenreService, get_genre_service

FILM_CACHE_EXPIRE_IN_SECONDS = 60

router = APIRouter()


@router.get("", response_model=list[Genre], summary="Genres")
@redis_cache(Genre, expired=FILM_CACHE_EXPIRE_IN_SECONDS)
async def get_many(
    request: Request,
    service: GenreService = Depends(get_genre_service),
    page_num: int = 1,
    page_size: int = 26,
) -> list[Genre]:
    """All genres"""
    objs = await service.search(
        page_num=page_num,
        page_size=page_size,
    )
    validate_not_found(objs, "genre_not_found")
    return [Genre(**x.dict()) for x in objs]


@router.get("/{genre_id}", response_model=Genre, summary="Genre detail information")
@redis_cache(Genre, expired=FILM_CACHE_EXPIRE_IN_SECONDS)
async def details(
    request: Request, genre_id: str, service: GenreService = Depends(get_genre_service)
) -> Genre:
    """Get detail genre information"""
    obj = await service.get_by_id(genre_id)
    validate_not_found(obj, "genre_not_found")
    return Genre(**obj.dict())
