import json
import os
from slugify import slugify
from .config import GENESIS_HOST, GENESIS_PORT
import requests
from zou.app.services import (
                                edits_service,
                                entities_service,
                            )
from .utils import update_edit_data

def handle_event(data):
    project_id = data['project_id']
    edit_id = data['edit_id']

    edit = edits_service.get_edit(edit_id)
    edit_name = edit['name']
    entity_type = entities_service.get_entity_type(edit['entity_type_id'])
    edit_file_name = slugify(edit_name, separator="_")
    edit_info = {'file_name': edit_file_name}
    update_edit_data(edit_id, edit_info)

    parent_id = edit['parent_id']
    if parent_id:
        genesys_parent = requests.get(
            url=f"{GENESIS_HOST}:{GENESIS_PORT}/data/entities",
            params={"secondary_id": parent_id}, timeout=5).json()[0]
        genesys_parent_id = genesys_parent['id']
    else:
        genesys_parent_id = None

    genesys_entity_type = requests.get(
        url=f"{GENESIS_HOST}:{GENESIS_PORT}/data/entity_types",
        params={"name": entity_type['name']}, timeout=5).json()[0]
    
    if not genesys_entity_type:
        payload = {
            "name": entity_type['name'],
        }
        genesys_entity_type = requests.post(url=f"{GENESIS_HOST}:{GENESIS_PORT}/data/entity_types", json=payload, timeout=5)

    genesys_entity_type_id = genesys_entity_type['id']

    genesys_project = requests.get(
        url=f"{GENESIS_HOST}:{GENESIS_PORT}/data/projects",
        params={"secondary_id": project_id}, timeout=5).json()[0]
    
    genesys_project_id = genesys_project['id']

    payload = {
        "name": edit_name,
        "secondary_id": edit_id,
        "project_id": genesys_project_id,
        "entity_type_id": genesys_entity_type_id,
        "parent_id": genesys_parent_id,
    }
    requests.post(url=f"{GENESIS_HOST}:{GENESIS_PORT}/data/entities", json=payload, timeout=5)