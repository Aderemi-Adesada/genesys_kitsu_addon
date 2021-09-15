from .config import GENESIS_HOST, GENESIS_PORT, SVN_SERVER_PARENT_URL, FILE_MAP
import requests
import json
import os
from slugify import slugify
from zou.app.services import (
                                projects_service,
                            )


def handle_event(data):
    project_id = data['project_id']

    project = projects_service.get_project(project_id)
    project_name = project['name']
    project_file_name = slugify(project_name, separator="_")
    
    svn_url = os.path.join(SVN_SERVER_PARENT_URL, project_file_name)
    if project['production_type'] == 'tvshow':
        file_tree_dir = os.path.join(os.path.dirname(__file__), 'eaxum_tv_show.json')
        with open(file_tree_dir, 'r') as f:
            file_tree = json.load(f)
        project_data =  {'file_tree': file_tree, 'data': {'file_map': FILE_MAP, 'svn_url': svn_url}}
        projects_service.update_project(project_id, project_data)
    else:
        file_tree_dir = os.path.join(os.path.dirname(__file__), 'eaxum.json')
        with open(file_tree_dir, 'r') as f:
            file_tree = json.load(f)
        project_data =  {'file_tree': file_tree, 'data': {'file_map': FILE_MAP, 'svn_url': svn_url}}
        projects_service.update_project(project_id, project_data)

    requests.post(url=f"{GENESIS_HOST}:{GENESIS_PORT}/project/{project_file_name}")

    data_dir = os.path.join(os.path.dirname(__file__), 'data.json')
    with open(data_dir, 'r') as f:
        genesys_data = json.load(f)
    genesys_data[project_id] = {'file_map': FILE_MAP, 'svn_url': svn_url, 'file_name': project_file_name, 'closed': False, 'assets': {}, 'shots': {}}

    with open(data_dir, 'w') as f:
        json.dump(genesys_data, f, indent=2)