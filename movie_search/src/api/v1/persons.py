from api.tools import validate_not_found
from api.v1.schemes import FullPerson, ShortFilm, ShortPerson
from db.redis import redis_cache
from fastapi import APIRouter, Depends, Query, Request
from services.film import FilmService, get_film_service
from services.person import PersonService, get_person_service

FILM_CACHE_EXPIRE_IN_SECONDS = 60

router = APIRouter()


@router.get("/search", response_model=list[FullPerson], summary="Person search")
@redis_cache(FullPerson, expired=FILM_CACHE_EXPIRE_IN_SECONDS)
async def search(
    request: Request,
    service: PersonService = Depends(get_person_service),
    page_num: int = 1,
    page_size: int = 50,
    query: str | None = Query(default=None, description="Person name"),
) -> list[FullPerson]:
    """Person search"""

    objs = await service.search(page_num=page_num, page_size=page_size, query=query)
    validate_not_found(objs, "person_not_found")
    return [FullPerson(**x.dict()) for x in objs]


@router.get(
    "/{person_id}", response_model=FullPerson, summary="Detail person information"
)
@redis_cache(FullPerson, expired=FILM_CACHE_EXPIRE_IN_SECONDS)
async def details(
    request: Request,
    person_id: str,
    service: PersonService = Depends(get_person_service),
) -> FullPerson:
    """Get detail movie information"""
    obj = await service.get_by_id(person_id)
    validate_not_found(obj, "person_not_found")
    return FullPerson(**obj.dict())


@router.get(
    "/{person_id}/film",
    response_model=list[ShortFilm],
    summary="Filter movies by person",
)
@redis_cache(ShortFilm, expired=FILM_CACHE_EXPIRE_IN_SECONDS)
async def get_by_person(
    request: Request,
    person_id: str,
    page_num: int = 1,
    service: FilmService = Depends(get_film_service),
    page_size: int = 50,
) -> list[ShortPerson]:
    """Get movies by person"""
    objs = await service.search(
        page_num=page_num, page_size=page_size, filter_film_by_person_id=person_id
    )
    validate_not_found(objs, "film_not_found")
    return [ShortFilm(**x.dict()) for x in objs]
