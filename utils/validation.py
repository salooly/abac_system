from typing import List, Union

from fastapi import HTTPException

from dal import DBClient
from dal.consts import USERS_COLLECTION, RESOURCES_COLLECTION, POLICIES_COLLECTION
from structures import Condition
from utils import AttributesHelper
from utils.consts import TYPES_MAPPING, OPERATORS_ALLOWED_TYPES
from utils.helpers.policies import PoliciesHelper
from utils.operators import OPERATORS_FUNCTIONS_MAPPING


def validate_attributes_type(attributes: dict):
    """
    validate that the attributes are indeed matching the Attribute object data type
    :param attributes: dict of attributes
    :return:
    """
    for key, value in attributes.items():
        attribute = AttributesHelper[key]
        attribute_type: type = attribute.get('attribute_type')
        if isinstance(value, TYPES_MAPPING.get(attribute_type)):
            continue

        raise HTTPException(
            status_code=404,
            detail=f'Invalid input. {key} is supposed to be of type {attribute_type}',
        )


def validate_policy_ids(policy_ids: list):
    """
    Validate that each policy ID indeed exists in the DB
    :param policy_ids:
    :return:
    """
    for policy_id in (policy_ids or []):
        if not PoliciesHelper.exists(policy_id):
            raise HTTPException(status_code=404, detail=f'Policy ID {policy_id} not found')


def validate_conditions(conditions: List[Condition]):
    """
    Validate that the conditions are valid. this checks that the attribute values and names match
    :param conditions:
    :return:
    """
    for condition in conditions:
        if not isinstance(condition, Condition):
            raise HTTPException(status_code=404, detail='Invalid input for condition')

        attribute_name: str = condition.attribute_name
        value: Union[str, bool, int] = condition.value
        operator: str = condition.operator.value
        validate_attributes_type({attribute_name: value})
        if type(value) not in OPERATORS_ALLOWED_TYPES.get(operator):
            raise HTTPException(status_code=404, detail=f'{operator} operator is not supported for {attribute_name}')


def _policy_is_met(attributes: dict, policy_id: str):
    """
    check if the attributes are meeting the policy requirements
    :param attributes: dict of attributes
    :param policy_id: id of the policy
    :return:
    """
    policy: dict = DBClient.search_for_id(collection=POLICIES_COLLECTION, id_value=policy_id)
    conditions: list = policy.get('conditions')
    if not conditions:
        return True  # if no condition for the policy everything meets it

    for condition in conditions:
        attribute: Union[str, bool, int] = attributes.get(condition['attribute_name'])
        if not attribute:
            return False  # if the user doesn't have the attribute at all then it doesn't suit

        operator_function = OPERATORS_FUNCTIONS_MAPPING.get(condition['operator'])  # run the operator function
        if not operator_function(attribute, condition['value']):
            return False

    return True


def authorize_user(user_id: str, resource_id: str) -> bool:
    """
    check if a user is authorized to reach a certain resource
    :param user_id: user id
    :param resource_id: resource id
    :return:
    """
    user: dict = DBClient.search_for_id(collection=USERS_COLLECTION, id_value=user_id)
    user_attributes: dict = user.get('attributes')
    resource: dict = DBClient.search_for_id(collection=RESOURCES_COLLECTION, id_value=resource_id)
    resource_policies: list = resource.get('policy_ids')
    if not resource_policies:
        return True  # if the resource has no policies then it's probably public

    for policy_id in resource_policies:
        if not _policy_is_met(attributes=user_attributes, policy_id=policy_id):
            return False

    return True
