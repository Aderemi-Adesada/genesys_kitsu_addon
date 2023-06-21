from .config import GENESIS_HOST, GENESIS_PORT
import requests
import os
from slugify import slugify
from zou.app.services import (
                                tasks_service,
                            )
from .utils import get_full_task

def handle_event(data):
    project_id = data['project_id']

    task = get_full_task(data['task_id'])
    task_type = tasks_service.get_task_type(task['task_type_id'])
    task_type_name = task_type['name'].lower()

    entity_id = task["entity_id"]
    genesys_entity = requests.get(
        url=f"{GENESIS_HOST}:{GENESIS_PORT}/data/entities",
        params={"secondary_id": entity_id}, timeout=5).json()[0]
    task_payload = {
        "name": f"{genesys_entity['name']}_{task_type_name}",
        "secondary_id": task['id'],
        "entity_id": genesys_entity['id'],
    }
    genesys_task = requests.post(url=f"{GENESIS_HOST}:{GENESIS_PORT}/data/tasks", json=task_payload, timeout=5)
    genesys_task = genesys_task.json()

    file_payload = {
        "name": genesys_task['name'],
        "task_id": genesys_task['id'],
        "software": "blender",
        "software_version": "2.80",
    }
    requests.post(url=f"{GENESIS_HOST}:{GENESIS_PORT}/data/files", json=file_payload, timeout=5)

    














    # try:
    #     old_project_file_name = genesys_data[project_id]['file_name']
    #     if old_project_file_name != project_file_name:
    #         payload = {
    #             'old_project_name':old_project_file_name,
    #             'new_project_name':project_file_name
    #             }
    #         # requests.put(url=f"{GENESIS_HOST}:{GENESIS_PORT}/project/{project_name}", json=payload)

    #         genesys_data[project_id]['file_name'] = project_file_name
    #         genesys_data[project_id]['svn_url'] = svn_url
    #         with open(data_dir, 'w') as file:
    #             json.dump(genesys_data, file)
            
    #         print(genesys_data)
    # except KeyError:
    #     print(genesys_data)
    #     print("Project not found in genesys")