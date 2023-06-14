import requests
from .config import GENESIS_HOST, GENESIS_PORT
from slugify import slugify
from zou.app.services import (
                                shots_service,
                                entities_service,
                            )
from .utils import update_sequence_data

def handle_event(data):
    project_id = data['project_id']
    sequence_id = data['sequence_id']
    sequence = shots_service.get_sequence(sequence_id)
    sequence_name = sequence['name']
    entity_type = entities_service.get_entity_type(sequence['entity_type_id'])
    sequence_file_name = slugify(sequence_name, separator="_")
    sequence_info = {'file_name': sequence_file_name}
    update_sequence_data(sequence_id, sequence_info)

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
        "name": sequence_name,
        "secondary_id": sequence_id,
        "project_id": genesys_project_id,
        "entity_type_id": genesys_entity_type_id,
    }
    requests.post(url=f"{GENESIS_HOST}:{GENESIS_PORT}/data/entities", json=payload, timeout=5)