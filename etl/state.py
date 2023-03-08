import abc
import json
from typing import Any, Optional

from bson import json_util


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
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
        """Сохранить состояние в постоянное хранилище"""
        with open(self.file_path, "r") as f:
            data = json.load(f)
            data.update(state)

        with open(self.file_path, "w") as f:
            json.dump(data, f, default=json_util.default)

    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
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
    Класс для хранения состояния при работе с данными, чтобы постоянно не перечитывать данные с начала.
    Здесь представлена реализация с сохранением состояния в файл.
    В целом ничего не мешает поменять это поведение на работу с БД или распределённым хранилищем.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        self.storage.save_state({key: value})

    def get_state(self, key: str) -> Any:
        data = self.storage.retrieve_state()
        return data.get(key)
