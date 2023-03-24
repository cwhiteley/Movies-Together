import backoff
import elasticsearch
from elasticsearch import Elasticsearch, helpers

import app_logger
from config import settings
from postgres_extractor import PostgresExtractor
from state import JsonFileStorage, State

psql_ext = PostgresExtractor(dsl=settings.postgres_movies.dict(), db_check_delay=10)
json_storage = JsonFileStorage(file_path="my_state")
state = State(storage=json_storage)
logger = app_logger.get_logger(__name__)


def state_management(states_dict: dict):
    """Getting dict such as {state_name: datetime} and save state"""
    for state_name, datetime in states_dict.items():
        state.set_state(key=state_name, value=datetime)


class ElasticSaver:
    """Load data from postgresql and save to elasticsearch"""

    def __init__(self, hosts: str):
        self.es = Elasticsearch(hosts)

    @backoff.on_exception(backoff.expo, elasticsearch.ConnectionError, logger=logger)
    async def save_filmwork_data(self, bunch_size: int) -> None:
        """Convert filmwork pydantic classes to dict and save to elasticsearch"""
        movies_generator = psql_ext.extract_filmwork(bunch_size)

        # Ready data for saving to elastic
        documents_list = []
        async for movie_list in movies_generator:
            my_movie_list, states_dict = movie_list
            for movie_data in my_movie_list:
                movie = {
                    "_id": movie_data.id,
                    "id": movie_data.id,
                    "imdb_rating": movie_data.imdb_rating,
                    "genre": movie_data.genre,
                    "title": movie_data.title,
                    "description": movie_data.description,
                    "directors_names": movie_data.directors_names,
                    "actors_names": movie_data.actors_names,
                    "writers_names": movie_data.writers_names,
                    "actors": movie_data.actors,
                    "writers": movie_data.writers,
                    "directors": movie_data.directors,
                }
                documents_list.append(movie)
            try:
                helpers.bulk(self.es, documents_list, index="movies")
                documents_list.clear()

                # If data added to elastic, save state
                state_management(states_dict)
            except elasticsearch.NotFoundError as err:
                logger.critical(err)
            except elasticsearch.SerializationError as err:
                logger.error(err)
            except elasticsearch.TransportError as err:
                logger.error(err)
            except Exception as err:
                logger.exception(err)

    @backoff.on_exception(backoff.expo, elasticsearch.ConnectionError, logger=logger)
    async def save_genres_data(self) -> None:
        """Convert genres pydantic classes to dict and save to elasticsearch"""
        genre_generator = psql_ext.extract_genres_data()

        # Ready data for saving to elastic
        documents_list = []
        async for genre_list in genre_generator:
            my_genre_list, genre_state = genre_list
            for genre_data in my_genre_list:
                genre = {
                    "_id": genre_data.id,
                    "id": genre_data.id,
                    "name": genre_data.name,
                }
                documents_list.append(genre)
            try:
                helpers.bulk(self.es, documents_list, index="genres")
                documents_list.clear()

                # If data added to elastic, save state
                state.set_state(key="genres_state", value=genre_state)
            except elasticsearch.NotFoundError as err:
                logger.critical(err)
            except elasticsearch.SerializationError as err:
                logger.error(err)
            except elasticsearch.TransportError as err:
                logger.error(err)
            except Exception as err:
                logger.exception(err)

    @backoff.on_exception(backoff.expo, elasticsearch.ConnectionError, logger=logger)
    async def save_persons_data(self, bunch_size: int) -> None:
        """Convert person pydantic classes to dict and save to elasticsearch"""
        person_generator = psql_ext.extract_persons_data(bunch_size)

        # Ready data for saving to elastic
        documents_list = []
        async for persons_list in person_generator:
            my_person_list, genre_state = persons_list
            for person_data in my_person_list:
                genre = {
                    "_id": person_data.id,
                    "id": person_data.id,
                    "full_name": person_data.full_name,
                    "roles": person_data.roles,
                    "film_ids": person_data.film_ids,
                }
                documents_list.append(genre)
            try:
                helpers.bulk(self.es, documents_list, index="persons")
                documents_list.clear()

                # If data added to elastic, save state
                state.set_state(key="persons_state", value=genre_state)
            except elasticsearch.NotFoundError as err:
                logger.critical(err)
            except elasticsearch.SerializationError as err:
                logger.error(err)
            except elasticsearch.TransportError as err:
                logger.error(err)
            except Exception as err:
                logger.exception(err)
