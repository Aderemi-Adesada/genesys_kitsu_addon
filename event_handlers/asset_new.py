import requests
from .config import GENESIS_HOST, GENESIS_PORT
from zou.app.services import (
                                assets_service,
                                entities_service,
                            )
from .utils import update_asset_data

def handle_event(data):
    project_id = data['project_id']
    asset_id = data['asset_id']
    asset = assets_service.get_asset(asset_id)
    asset_name = asset['name']
    entity_type = entities_service.get_entity_type(asset['entity_type_id'])

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
        "name": asset_name,
        "secondary_id": asset_id,
        "project_id": genesys_project_id,
        "entity_type_id": genesys_entity_type_id,
    }
    requests.post(url=f"{GENESIS_HOST}:{GENESIS_PORT}/data/entities", json=payload, timeout=5)