import requests
from .config import GENESIS_HOST, GENESIS_PORT
from slugify import slugify
from zou.app.services import (
                                shots_service,
                                entities_service,
                            )
from .utils import update_episode_data

def handle_event(data):
    project_id = data['project_id']
    episode_id = data['episode_id']
    episode = shots_service.get_episode(episode_id)
    episode_name = episode['name']
    entity_type = entities_service.get_entity_type(episode['entity_type_id'])
    episode_file_name = slugify(episode_name, separator="_")
    episode_info = {'file_name': episode_file_name}
    update_episode_data(episode_id, episode_info)

    parent_id = episode['parent_id']
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
        "name": episode_name,
        "secondary_id": episode_id,
        "project_id": genesys_project_id,
        "entity_type_id": genesys_entity_type_id,
        "parent_id": genesys_parent_id,
    }
    requests.post(url=f"{GENESIS_HOST}:{GENESIS_PORT}/data/entities", json=payload, timeout=5)