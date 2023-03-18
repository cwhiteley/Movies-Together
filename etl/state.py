import abc
import json
from typing import Any, Optional

from bson import json_util


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Save state to persistent storage"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Load state locally from persistent storage"""
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def create_initial_state(self):
        """Creating file with minimal state datetime"""
        with open(self.file_path, "w") as f:
            json.dump(
                {
                    "filmwork_person_state": {"$date": "2000-01-01T19:43:57.714Z"},
                    "filmwork_state": {"$date": "2000-01-16T20:14:09.271Z"},
                    "filmwork_genre_state": {"$date": "2000-01-01T19:42:35.487Z"},
                    "genres_state": {"$date": "2000-01-01T19:42:35.487Z"},
                    "persons_state": {"$date": "2000-01-01T19:42:35.487Z"},
                },
                f,
                default=json_util.default,
            )

    def save_state(self, state: dict) -> None:
        """Save state to persistent storage"""
        with open(self.file_path, "r") as f:
            data = json.load(f)
            data.update(state)

        with open(self.file_path, "w") as f:
            json.dump(data, f, default=json_util.default)

    def retrieve_state(self) -> dict:
        """Load state locally from persistent storage"""
        try:
            with open(self.file_path) as f:
                data = json.load(f, object_hook=json_util.object_hook)
                return data
        except FileNotFoundError:  # если в хранилище нет данных
            self.create_initial_state()
            with open(self.file_path) as f:
                data = json.load(f, object_hook=json_util.object_hook)
                return data


class State:
    """
    A class for storing state when working with data, so as not to constantly re-read the data from the beginning.
    Here is a stateful-to-file implementation.
    In general, nothing prevents changing this behavior to work with a database or distributed storage.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Set the state for a specific key"""
        self.storage.save_state({key: value})

    def get_state(self, key: str) -> Any:
        data = self.storage.retrieve_state()
        return data.get(key)
