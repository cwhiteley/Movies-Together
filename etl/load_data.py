import asyncio
import subprocess

from config import settings
from elastic_saver import ElasticSaver


async def load_data():
    """
    Load data from Postgres to Elasticsearch using asynchronous tasks.

    The data is loaded using the ElasticSaver class, which saves the data to Elasticsearch.
    This function creates three asynchronous tasks to save genres, filmworks, and persons data.
    """

    elastic_saver = ElasticSaver(f"http://{settings.elastic.site}:{settings.elastic.port}")

    tasks = [
        asyncio.create_task(elastic_saver.save_genres_data()),
        asyncio.create_task(elastic_saver.save_filmwork_data(bunch_size=400)),
        asyncio.create_task(elastic_saver.save_persons_data(bunch_size=500)),
    ]

    await asyncio.gather(*tasks)


def create_elasticsearch_indexes():
    """
    Create Elasticsearch indexes using the create_elastic_indexes.sh script.
    """
    subprocess.run(["sh", "create_elastic_indexes.sh"])


if __name__ == "__main__":
    create_elasticsearch_indexes()

    # Wait for a few seconds for Elasticsearch to start
    asyncio.sleep(5)

    # Load data from Postgres to Elasticsearch
    asyncio.run(load_data())
