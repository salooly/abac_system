import os
from enum import Enum
from typing import Generator

from pymongo import MongoClient

from dal.consts import (DB_NAME, MONGO_HOST, MONGO_PASSWORD, MONGO_PORT,
                        MONGO_USERNAME)


def dictify(raw_dict: dict):
    """
    Since some of the data is actually Enums we need to parse it to make sure it's flat for the DB
    :param raw_dict:
    :return:
    """
    new_dict: dict = {}
    for key, value in raw_dict.items():
        if isinstance(value, Enum):
            value = value.value
            new_dict[key] = value
        elif isinstance(value, dict):
            new_dict[key] = dictify(value)
        elif isinstance(value, list):
            new_dict[key] = []
            for cell in value:
                if isinstance(cell, dict):
                    new_dict[key].append(dictify(cell))
                else:
                    new_dict[key].append(cell)
        else:
            new_dict[key] = value
    return new_dict


class DBClient:
    """
    Singleton DB Client handler
    """
    _client = MongoClient(
        host=os.environ.get(MONGO_HOST),
        port=os.environ.get(MONGO_PORT),
        username=os.environ.get(MONGO_USERNAME),
        password=os.environ.get(MONGO_PASSWORD),
    )

    @classmethod
    def query(cls, collection: str, query: dict) -> Generator[dict, None, None]:
        for entity in cls._client[DB_NAME][collection].find(query):
            entity.pop('_id', None)
            yield entity

    @classmethod
    def update(cls, collection: str, update_filter: dict, document: dict, **kwargs):
        cls._client[DB_NAME][collection].update_one(
            filter=update_filter,
            update={
                '$set': dictify(document),
            },
            **kwargs,
        )

    @classmethod
    def remove(cls, collection: str, delete_filter: dict, projection: dict, **kwargs):
        cls._client[DB_NAME][collection].update_one(
            filter=delete_filter,
            update={
                '$unset': projection,
            },
            **kwargs,
        )

    @classmethod
    def save_to_db(cls, collection: str, id_field: str, document: dict, **kwargs):
        update_filter: dict = {
            '_id': document.get(id_field),
        }
        DBClient.update(
            collection=collection,
            document=document,
            update_filter=update_filter,
            upsert=True,
        )

    @classmethod
    def search_for_id(cls, collection: str, id_value: str):
        for document in DBClient.query(collection=collection, query={'_id': id_value}):
            return document
