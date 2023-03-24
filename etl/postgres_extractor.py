import asyncio
import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

import backoff
import psycopg
from psycopg.rows import class_row
from pydantic import BaseModel, validator

import app_logger
from state import JsonFileStorage, State

state = State(JsonFileStorage("my_state"))
logger = app_logger.get_logger(__name__)
my_handler = logging.StreamHandler()
logger.addHandler(my_handler)
logger.setLevel(logging.DEBUG)


# Pydantic configuration
class Movie(BaseModel):
    id: UUID
    imdb_rating: Optional[float] = 0.0
    genre: list[dict]
    title: str
    description: str = None
    directors_names: Optional[list[str]] = ""
    actors_names: list[str] = None
    writers_names: list[str] = None
    actors: list[dict] = None
    writers: list[dict] = None
    directors: list[dict] = None
    modified: datetime

    class Config:
        validate_assignment = True

    @validator("directors_names")
    def set_name(cls, directors_names):
        return directors_names or []


class Genre(BaseModel):
    id: UUID
    name: str
    modified: datetime


class Person(BaseModel):
    id: UUID
    full_name: str
    roles: list[str]
    film_ids: list[UUID]
    modified: datetime


class PostgresExtractor:
    """Extract data from postgres and pass to elasticsearch"""

    def __init__(self, dsl: dict, db_check_delay: int):
        self.dsl = dsl
        self.db_check_delay = db_check_delay
        self.postgres_monitor = PostgresMonitor(dsl)

    @backoff.on_exception(backoff.expo, psycopg.OperationalError, logger=logger)
    async def extract_filmwork(self, bunch_size: int) -> tuple:
        """Getting movie pydantic classes by latest state"""

        async with await psycopg.AsyncConnection.connect(
            **self.dsl, row_factory=class_row(Movie)
        ) as conn:
            async with conn.cursor() as cur:
                while True:
                    # Get last state
                    last_state = state.get_state("filmwork_state")

                    # Get ids and datetime state
                    (
                        genres_to_update,
                        genres_state,
                    ) = await self.postgres_monitor.genres_monitor(bunch_size)
                    (
                        persons_to_update,
                        persons_state,
                    ) = await self.postgres_monitor.persons_monitor(bunch_size)

                    # Tuple of IDs to update
                    film_works_to_update = genres_to_update + persons_to_update
                    # Check updates in genres and persons
                    if film_works_to_update == ():
                        or_statement = ""
                    else:
                        or_statement = f"OR film_work.id IN {film_works_to_update}"
                    try:
                        await cur.execute(
                            f"""
                            SELECT  "movies_content"."film_work"."id",
                                "movies_content"."film_work"."modified",
                                "movies_content"."film_work"."title",
                                "movies_content"."film_work"."description",
                                "movies_content"."film_work"."rating" as "imdb_rating",
                                Array_agg(DISTINCT "movies_content"."person"."full_name" ) filter (WHERE t6."role" = 'actor')    AS "actors_names",
                                array_agg(DISTINCT "movies_content"."person"."full_name" ) filter (WHERE t6."role" = 'director') AS "directors_names",
                                array_agg(DISTINCT "movies_content"."person"."full_name") filter (WHERE t6."role" = 'writer')   AS "writers_names",
                                JSON_AGG(DISTINCT jsonb_build_object('name', "movies_content"."person"."full_name", 'id', "movies_content"."person"."id")) filter (WHERE t6."role" = 'writer')  AS "writers",
                                JSON_AGG(DISTINCT jsonb_build_object('name', "movies_content"."person"."full_name", 'id', "movies_content"."person"."id")) filter (WHERE t6."role" = 'actor')  AS "actors",
                                JSON_AGG(DISTINCT jsonb_build_object('name', "movies_content"."person"."full_name", 'id', "movies_content"."person"."id")) filter (WHERE t6."role" = 'director')  AS "directors",
                                JSON_AGG(DISTINCT jsonb_build_object('name', "movies_content"."genre"."name", 'id', "movies_content"."genre"."id")) AS "genre"

                        FROM            "movies_content"."film_work"
                        left outer join "movies_content"."genre_film_work"
                        ON              (
                                                        "movies_content"."film_work"."id" = "movies_content"."genre_film_work"."film_work_id")
                        left outer join "movies_content"."genre"
                        ON              (
                                                        "movies_content"."genre_film_work"."genre_id" = "movies_content"."genre"."id")
                        left outer join "movies_content"."person_film_work"
                        ON              (
                                                        "movies_content"."film_work"."id" = "movies_content"."person_film_work"."film_work_id")
                        left outer join "movies_content"."person"
                        ON              (
                                                        "movies_content"."person_film_work"."person_id" = "movies_content"."person"."id")
                        left outer join "movies_content"."person_film_work" t6
                        ON              (
                                                        "movies_content"."person"."id" = t6."person_id")
                        WHERE film_work.modified >= '{last_state}' {or_statement}
                        GROUP BY film_work.id
                        ORDER BY film_work.modified

                        LIMIT {bunch_size};
                            """
                        )
                        result = await cur.fetchall()
                        new_state = result[-1].modified

                        # Creating a dict to further update the state
                        states_dict = {}
                        (
                            states_dict["filmwork_state"],
                            states_dict["filmwork_genre_state"],
                            states_dict["filmwork_person_state"],
                        ) = (new_state, genres_state, persons_state)

                        await asyncio.sleep(self.db_check_delay)
                        yield result, states_dict
                    except IndexError:
                        pass
                    except Exception as err:
                        await logger.error(err)

    @backoff.on_exception(backoff.expo, psycopg.OperationalError, logger=logger)
    async def extract_genres_data(self) -> tuple:
        """Getting genres pydantic classes by latest state"""

        async with await psycopg.AsyncConnection.connect(
            **self.dsl, row_factory=class_row(Genre)
        ) as conn:
            # Open a cursor to perform database operations
            async with conn.cursor() as cur:
                while True:
                    # Get last save datetime
                    last_state = state.get_state("genres_state")

                    try:
                        await cur.execute(
                            f"""
                                SELECT
                                    id,
                                    name,
                                    modified
                                FROM
                                    "movies_content"."genre"
                                    WHERE
                                    "modified" > '{last_state}'
                                ORDER BY
                                    "modified";

                            """
                        )
                        result = await cur.fetchall()
                        new_state = result[-1].modified

                        await asyncio.sleep(self.db_check_delay)
                        yield result, new_state
                    except IndexError:
                        pass
                    except Exception as err:
                        await logger.error(err)

    @backoff.on_exception(backoff.expo, psycopg.OperationalError, logger=logger)
    async def extract_persons_data(self, bunch_size: int) -> tuple:
        """Getting persons pydantic classes by latest state"""

        async with await psycopg.AsyncConnection.connect(
            **self.dsl, row_factory=class_row(Person)
        ) as conn:
            # Open a cursor to perform database operations
            async with conn.cursor() as cur:
                while True:
                    # Get last save datetime
                    last_state = state.get_state("persons_state")

                    try:
                        await cur.execute(
                            f"""
                                SELECT
                                    person.id,
                                    person.full_name,
                                    person.modified,
									Array_agg(DISTINCT "movies_content"."person_film_work"."role" ) AS roles,
									Array_agg(DISTINCT "movies_content"."person_film_work"."film_work_id" ) AS film_ids
                                FROM
                                    movies_content.person
                                LEFT OUTER JOIN movies_content.person_film_work
                                	ON movies_content.person.id = movies_content.person_film_work.person_id
                                	
                                WHERE movies_content.person.modified >= '{last_state}'
                           
                                GROUP BY movies_content.person.id
                                ORDER BY movies_content.person.modified
                                
                                LIMIT {bunch_size};

                            """
                        )
                        result = await cur.fetchall()
                        new_state = result[-1].modified

                        await asyncio.sleep(self.db_check_delay)
                        yield result, new_state
                    except IndexError:
                        pass
                    except Exception as err:
                        await logger.error(err)


class PostgresMonitor:
    """Updates monitoring in postgresql"""

    def __init__(self, dsl):
        self.dsl = dsl

    async def genres_monitor(self, bunch_size: int) -> tuple:
        """Checking for genre updates and getting movies IDs"""
        try:
            async with await psycopg.AsyncConnection.connect(**self.dsl) as conn:
                async with conn.cursor() as cur:
                    last_state = state.get_state("filmwork_genre_state")
                    await cur.execute(
                        f"""SELECT
                      "movies_content"."film_work"."id",
                      MAX(
                        "movies_content"."genre"."modified"
                      ) AS "modified"
                    FROM
                      "movies_content"."film_work"
                      left outer join "movies_content"."genre_film_work" ON (
                        "movies_content"."film_work"."id" = "movies_content"."genre_film_work"."film_work_id"
                      )
                      left outer join "movies_content"."genre" ON (
                        "movies_content"."genre_film_work"."genre_id" = "movies_content"."genre"."id"
                      )
                    WHERE
                      "movies_content"."genre".modified > '{last_state}'
                    GROUP BY
                      film_work.id
                    ORDER BY
                      modified
                    LIMIT
                      {bunch_size};
                    """
                    )
                    result = await cur.fetchall()
                    # Get last modified field for state update
                    genres_state = result[-1][1]
                    result = [i[0] for i in result]
                    return tuple(result), genres_state

        except IndexError:
            return ()
        except Exception as err:
            await logger.error(err)

    async def persons_monitor(self, bunch_size: int) -> tuple:
        """Checking for person updates and getting movies IDs"""
        try:
            async with await psycopg.AsyncConnection.connect(**self.dsl) as conn:
                async with conn.cursor() as cur:
                    last_state = state.get_state("filmwork_person_state")
                    await cur.execute(
                        f"""SELECT
                      "movies_content"."film_work"."id",
                      MAX(
                        "movies_content"."person"."modified"
                      ) AS "modified"
                    FROM
                      "movies_content"."film_work"
                      RIGHT OUTER JOIN "movies_content"."person_film_work" ON (
                        "movies_content"."film_work"."id" = "movies_content"."person_film_work"."film_work_id"
                      )
                      RIGHT OUTER JOIN "movies_content"."person" ON (
                        "movies_content"."person_film_work"."person_id" = "movies_content"."person"."id"
                      )
                      RIGHT OUTER JOIN "movies_content"."person_film_work" t6 ON (
                        "movies_content"."person"."id" = t6."person_id"
                      )
                    WHERE
                      "movies_content"."person".modified > '{last_state}'
                    GROUP BY
                      film_work.id
                    ORDER BY
                      modified
                    LIMIT
                      {bunch_size};
                    """
                    )
                    result = await cur.fetchall()
                    # Get last modified field for state update
                    person_state = result[-1][1]
                    result = [i[0] for i in result]

                    return tuple(result), person_state
        except IndexError:
            return ()
        except Exception as err:
            await logger.error(err)
