from models.base import CinemaModel


class GenreInFilm(CinemaModel):
    """Genre model inside film"""

    id: str
    name: str


class PersonInFilm(CinemaModel):
    """Person model inside film"""

    id: str
    name: str


class Film(CinemaModel):
    id: str
    title: str
    description: str | None
    imdb_rating: float
    genre: list[GenreInFilm]

    directors_names: list[str] | None
    actors_names: list[str] | None
    writers_names: list[str] | None

    actors: list[PersonInFilm] | None
    writers: list[PersonInFilm] | None
    directors: list[PersonInFilm] | None
