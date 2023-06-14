from .config import GENESIS_HOST, GENESIS_PORT
import requests
import json
import os
from slugify import slugify
from zou.app.services import (
                                projects_service,
                                shots_service,
                            )
from .utils import update_episode_data

def handle_event(data):
    project_id = data['project_id']
    episode_id = data['episode_id']
    project = projects_service.get_project(project_id)

    episode = shots_service.get_episode(episode_id)
    episode_name = episode['name']
    episode_file_name = slugify(episode_name, separator="_")
    project_name = slugify(project['name'], separator='_')

    if 'file_name' in episode['data'].keys():
        old_episode_file_name = episode['data']['file_name']
    else:
        episode_info = {'file_name': episode_file_name}
        update_episode_data(episode_id, episode_info)
        old_episode_file_name = episode_file_name

    if old_episode_file_name != episode_file_name:
        payload = {"name": episode_name,"secondary_id": episode_id}
        requests.put(url=f"{GENESIS_HOST}:{GENESIS_PORT}/data/entities", json=payload, timeout=5)

        episode_info = {'file_name': episode_file_name}
        update_episode_data(episode_id, episode_info)