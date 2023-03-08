from models.base import CinemaModel


class Person(CinemaModel):
    """Genre model"""

    id: str
    full_name: str
    roles: list[str]
    film_ids: list[str]
