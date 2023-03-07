from pydantic import BaseModel, Field


class UuidModel(BaseModel):
    id: str = Field(alias="uuid")

    class Config:
        allow_population_by_field_name = True


class Genre(UuidModel):
    name: str


class ShortPerson(UuidModel):
    name: str = Field(alias="full_name")


class FullPerson(ShortPerson):
    roles: list[str]
    film_ids: list[str]


class ShortFilm(UuidModel):
    title: str
    imdb_rating: float


class FullFilm(ShortFilm):
    genre: list[Genre]
    actors: list[ShortPerson] | None
    writers: list[ShortPerson] | None
    directors: list[ShortPerson] | None
