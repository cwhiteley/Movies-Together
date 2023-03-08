from models.base import CinemaModel


class Genre(CinemaModel):
    """Genre model"""

    id: str
    name: str
    description: str | None
