from typing import List

from fastapi import FastAPI, HTTPException

from dal import DBClient
from dal.consts import (ATTRIBUTES_COLLECTION, POLICIES_COLLECTION,
                        RESOURCES_COLLECTION, USERS_COLLECTION)
from structures import Attribute, Condition, Policy, Resource, User
from utils import AttributesHelper
from utils.validation import (validate_attributes_type, validate_conditions,
                              validate_policy_ids, authorize_user)

app = FastAPI()


@app.post('/attributes', tags=['attributes'])
async def create_attribute(attribute: Attribute):
    existing_attribute = None
    attribute_name: str = attribute.attribute_name
    try:
        existing_attribute = AttributesHelper[attribute_name]
    except Exception:
        pass
    if existing_attribute:
        raise HTTPException(status_code=404, detail=f'Attribute {attribute_name} already exists')
    DBClient.save_to_db(collection=ATTRIBUTES_COLLECTION, id_field='attribute_name', document=attribute.model_dump())
    return {'message': 'Attribute created successfully'}


@app.get('/attributes/{attribute_name}', tags=['attributes'])
async def get_attribute(attribute_name: str):
    try:
        attribute = AttributesHelper[attribute_name]
        return attribute
    except Exception as e:
        error_message = f'{e}'
        raise HTTPException(status_code=404, detail=error_message)


@app.post('/users', tags=['users'])
async def create_user(user: User):
    for _ in DBClient.query(collection=USERS_COLLECTION, query={'_id': user.user_id}):
        raise HTTPException(status_code=404, detail='user already exists')
    validate_attributes_type(user.attributes or {})

    DBClient.save_to_db(collection=USERS_COLLECTION, id_field='user_id', document=user.model_dump())
    return {'message': 'User created successfully'}


@app.get('/users/{user_id}', tags=['users'])
async def get_user(user_id: str):
    user = DBClient.search_for_id(collection=USERS_COLLECTION, id_value=user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user


@app.put('/users/{user_id}', tags=['users'])
async def update_user_attributes(user_id: str, new_attributes: dict):
    validate_attributes_type(new_attributes or {})
    try:
        DBClient.update(
            collection=USERS_COLLECTION,
            update_filter={
                '_id': user_id,
            },
            document={
                'attributes': new_attributes,
            },
            upsert=False,
        )
    except Exception:
        raise HTTPException(status_code=404, detail='Resource not found')
    return {'message': 'User attributes updated successfully'}


@app.patch('/users/{user_id}/attributes/{attribute_name}', tags=['users'])
async def update_user_attribute(user_id: str, attribute_name: str, new_value: dict):
    new_value = new_value.get(attribute_name)
    validate_attributes_type({attribute_name: new_value})
    try:
        DBClient.update(
            collection=USERS_COLLECTION,
            update_filter={
                '_id': user_id,
            },
            document={
                f'attributes.{attribute_name}': new_value,
            },
            upsert=False,
        )
    except Exception:
        raise HTTPException(status_code=404, detail='Resource not found')
    return {'message': 'User attribute updated successfully'}


@app.delete('/users/{user_id}/attributes/{attribute_name}', tags=['users'])
async def delete_user_attribute(user_id: str, attribute_name: str):
    try:
        DBClient.remove(
            collection=USERS_COLLECTION,
            delete_filter={
                '_id': user_id,
            },
            projection={
                f'attributes.{attribute_name}': 1,
            },
            upsert=False,
        )
    except Exception:
        raise HTTPException(status_code=404, detail='Resource not found')
    return {'message': 'User attribute updated successfully'}


@app.post('/policies', tags=['policies'])
async def create_policy(policy: Policy):
    for _ in DBClient.query(collection=POLICIES_COLLECTION, query={'_id': policy.policy_id}):
        raise HTTPException(status_code=404, detail='policy already exists')
    validate_conditions(policy.conditions or [])

    DBClient.save_to_db(collection=POLICIES_COLLECTION, id_field='policy_id', document=policy.model_dump())
    return {'message': 'Policy created successfully'}


@app.get('/policies/{policy_id}', tags=['policies'])
async def get_policy(policy_id: str):
    policy = DBClient.search_for_id(collection=POLICIES_COLLECTION, id_value=policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail='Policy not found')
    return policy


@app.put('/policies/{policy_id}', tags=['policies'])
async def update_policy_conditions(policy_id: str, new_conditions: List[Condition]):
    validate_conditions(new_conditions or [])
    try:
        DBClient.update(
            collection=POLICIES_COLLECTION,
            update_filter={
                '_id': policy_id,
            },
            document={
                'conditions': [condition.model_dump() for condition in new_conditions],
            },
            upsert=False,
        )
    except Exception:
        raise HTTPException(status_code=404, detail='Policy not found')
    return {'message': 'Policy conditions updated successfully'}


@app.post('/resources', tags=['resource'])
async def create_resource(resource: Resource):
    for _ in DBClient.query(collection=RESOURCES_COLLECTION, query={'_id': resource.resource_id}):
        raise HTTPException(status_code=404, detail='resource already exists')
    validate_policy_ids(resource.policy_ids)  # validate that the policies exist

    DBClient.save_to_db(collection=RESOURCES_COLLECTION, id_field='resource_id', document=resource.model_dump())
    return {'message': 'Resource created successfully'}


@app.get('/resources/{resource_id}', tags=['resource'])
async def get_resource(resource_id: str):
    resource = DBClient.search_for_id(collection=RESOURCES_COLLECTION, id_value=resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail='Resource not found')
    return resource


@app.put('/resources/{resource_id}', tags=['resource'])
async def update_resource_policies(resource_id: str, new_policy_ids: List[str]):
    validate_policy_ids(new_policy_ids)
    try:
        DBClient.update(
            collection=RESOURCES_COLLECTION,
            update_filter={
                '_id': resource_id,
            },
            document={
                'policy_ids': new_policy_ids,
            },
            upsert=False,
        )
    except Exception:
        raise HTTPException(status_code=404, detail='Resource not found')

    return {'message': 'Resource policies updated successfully'}


@app.get('/is_authorized', tags=['authorize'])
async def read_item(user_id: str, resource_id: str):
    return {'decision': authorize_user(user_id=user_id, resource_id=resource_id)}
