import asyncio
import subprocess
from time import sleep

from config import settings
from elasctic_saver import ElasticSaver


async def load_data():
    """
    Load data from Postgres to Elasticsearch using asynchronous tasks.

    The data is loaded using the ElasticSaver class, which saves the data to Elasticsearch.
    This function creates three asynchronous tasks to save genres, filmworks, and persons data.
    """

    elastic_saver = ElasticSaver(
        f"http://{settings.elastic.site}:{settings.elastic.port}"
    )

    task = asyncio.create_task(elastic_saver.save_genres_data())
    task2 = asyncio.create_task(elastic_saver.save_filmwork_data(bunch_size=400))
    task3 = asyncio.create_task(elastic_saver.save_persons_data(bunch_size=500))
    await task
    await task2
    await task3


def create_elasctic_indexes():
    subprocess.run(["sh", "create_elastic_indexes.sh"])


if __name__ == "__main__":
    create_elasctic_indexes()
    sleep(2)
    asyncio.run(load_data())
