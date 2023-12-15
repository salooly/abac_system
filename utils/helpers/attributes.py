from functools import lru_cache

from fastapi import HTTPException

from dal import DBClient
from dal.consts import ATTRIBUTES_COLLECTION


def pull_all_attributes():
    """
    pull of the attributes from the db
    :return:
    """
    mapping: dict = {}
    for attribute in DBClient.query(collection=ATTRIBUTES_COLLECTION, query={}):
        mapping[attribute.get('_id')] = attribute
    return mapping


class AttributesHelper:
    """
    since the attributes are used a lot, they're fairly light and they are IMMUTABLE (and also not being deleted),
    I decided to create a class to store the values in the RAM in order to shorten runtime
    """
    _mapping: dict = pull_all_attributes()

    @classmethod
    @lru_cache
    def __class_getitem__(cls, key):
        if key in cls._mapping:
            return cls._mapping[key]

        for document in DBClient.query(collection=ATTRIBUTES_COLLECTION, query={'_id': key}):
            if not document:
                continue
            cls._mapping[key] = document
            return document

        raise HTTPException(status_code=404, detail=f'attribute {key} was not found')
