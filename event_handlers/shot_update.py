from .config import GENESIS_HOST, GENESIS_PORT
import requests
import json
import os
from slugify import slugify
from zou.app.services import (
                                projects_service,
                                shots_service,
                            )
from .utils import rename_task_file


def handle_event(data):
    project_id = data['project_id']
    shot_id = data['shot_id']
    project = projects_service.get_project(project_id)

    shot = shots_service.get_shot(shot_id)
    shot_name = shot['name']
    shot_file_name = slugify(shot_name, separator="_")
    project_name = slugify(project['name'], separator='_')

    data_dir = os.path.join(os.path.dirname(__file__), 'data.json')
    with open(data_dir) as file:
        genesys_data = json.load(file)

    try:
        genesys_project_data = genesys_data[project_id]
    except KeyError:
        print("Project not found in genesys")
        return
    try:
        old_shot_file_name = genesys_project_data['shots'][shot_id]['file_name']
    except KeyError:
        print(f"shot not found in project {project_id}")
        return
    if old_shot_file_name != shot_file_name:
        shots_service.clear_shot_cache(shot_id)
        full_shot = shots_service.get_full_shot(shot_id)
        shot_tasks = full_shot['tasks']
        if shot_tasks:
            payload = []
            for task in shot_tasks:
                rename_task_file(
                    new_name=shot_file_name,
                    old_name=old_shot_file_name,
                    task=task,
                    project=project,
                    payload=payload,
                    entity_type='shot'
                )
            requests.put(url=f"{GENESIS_HOST}:{GENESIS_PORT}/shot/{project_name}", json=payload)

        genesys_project_data['shots'][shot_id]['file_name'] = shot_file_name
        with open(data_dir, 'w') as file:
            json.dump(genesys_data, file, indent=2)