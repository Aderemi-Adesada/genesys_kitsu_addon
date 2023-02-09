from .config import GENESIS_HOST, GENESIS_PORT
import requests
import json
import os
from slugify import slugify
from zou.app.services import (
                                projects_service,
                                shots_service,
                            )
from .utils import rename_task_file, update_shot_data
from .utils import with_app_context

@with_app_context
def handle_event(data):
    project_id = data['project_id']
    shot_id = data['shot_id']
    project = projects_service.get_project(project_id)

    shot = shots_service.get_shot(shot_id)
    shot_name = shot['name']
    shot_file_name = slugify(shot_name, separator="_")
    project_name = slugify(project['name'], separator='_')

    if 'file_name' in shot['data'].keys():
        old_shot_file_name = shot['data']['file_name']
    else:
        shot_info = {'file_name': shot_file_name}
        update_shot_data(shot_id, shot_info)
        old_shot_file_name = shot_file_name

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

        shot_info = {'file_name': shot_file_name}
        update_shot_data(shot_id, shot_info)