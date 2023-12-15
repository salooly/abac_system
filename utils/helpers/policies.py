from functools import lru_cache

from dal import DBClient
from dal.consts import POLICIES_COLLECTION


def pull_all_policies_ids() -> set:
    """
    pull of the attributes from the db
    :return:
    """
    ids = set()
    for attribute in DBClient.query(collection=POLICIES_COLLECTION, query={}):
        ids.add(attribute.get('_id'))
    return ids


class PoliciesHelper:
    """
    since the policies are not deletable (at least as for now and as described in the exercise), and are only up to 10K
    keeping in memory the ids of the policies could help shorten time with the db
    """
    _ids: set = pull_all_policies_ids()

    @classmethod
    @lru_cache
    def exists(cls, policy_id: str):
        if policy_id in cls._ids:
            return True

        if DBClient.search_for_id(collection=POLICIES_COLLECTION, id_value=policy_id):
            cls._ids.add(policy_id)
            return True

        return False
