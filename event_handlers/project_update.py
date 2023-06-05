from .config import GENESIS_HOST, GENESIS_PORT
import requests
from zou.app.services import (
                                projects_service,
                            )
from slugify import slugify
from .utils import update_project_data

def handle_event(data):
    project_id = data['project_id']
    project = projects_service.get_project(project_id)
    project_name = project['name']

    project_file_name = slugify(project_name, separator="_")
    if not project['data']:
        project['data'] = {}
    if 'file_name' in project['data'].keys():
        old_project_file_name = project['data']['file_name']
    else:
        project_info = {'file_name': project_file_name}
        update_project_data(project_id, project_info)
        old_project_file_name = project_file_name

    if old_project_file_name != project_file_name:
        payload = {"name": project_name,"secondary_id": project_id}
        requests.put(url=f"{GENESIS_HOST}:{GENESIS_PORT}/data/projects", json=payload, timeout=5)
        
        project_info = {'file_name': project_file_name}
        update_project_data(project_id, project_info)