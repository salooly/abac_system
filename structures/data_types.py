from enum import Enum
from typing import Dict, List, Union

from pydantic import BaseModel


class AttributeDataTypes(Enum):
    string: str = 'string'
    boolean: str = 'boolean'
    integer: str = 'integer'


class ConditionOperators(Enum):
    equal: str = '='
    greater_than: str = '>'
    smaller_than: str = '<'
    starts_with: str = 'starts_with'


class Attribute(BaseModel):
    attribute_name: str
    attribute_type: AttributeDataTypes


class User(BaseModel):
    user_id: str
    attributes: Dict[str, Union[str, bool, int]] | None = None


class Condition(BaseModel):
    attribute_name: str
    operator: ConditionOperators
    value: Union[str, bool, int]


class Policy(BaseModel):
    policy_id: str
    conditions: List[Condition] | None = None


class Resource(BaseModel):
    resource_id: str
    policy_ids: List[str] | None = None
