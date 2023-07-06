from gazu.project import new_project
from .config import GENESIS_HOST, GENESIS_PORT, SVN_SERVER_PARENT_URL
import requests
import json
import os
from slugify import slugify
from zou.app.services import (
                                projects_service,
                            )
from .utils import update_project_data, with_app_context

@with_app_context
def handle_event(data):
    project_id = data['project_id']
    project = projects_service.get_project(project_id)

    project_name = project['name']
    project_file_name = slugify(project_name, separator="_")
    svn_url = os.path.join(SVN_SERVER_PARENT_URL, project_file_name)
    if not project['data']:
        project['data'] = {}
    if 'file_name' in project['data'].keys():
        old_project_file_name = project['data']['file_name']
    else:
        project_info = {'file_name': project_file_name}
        update_project_data(project_id, project_info)
        old_project_file_name = project_file_name

    if old_project_file_name != project_file_name:
        payload = {
            'old_project_name':old_project_file_name,
            'new_project_name':project_file_name
            }
        requests.put(url=f"{GENESIS_HOST}:{GENESIS_PORT}/project/{project_file_name}", json=payload)

        project_info = {'file_name': project_file_name}
        update_project_data(project_id, project_info)