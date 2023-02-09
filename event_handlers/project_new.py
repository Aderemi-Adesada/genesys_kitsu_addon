from .config import GENESIS_HOST, GENESIS_PORT, SVN_SERVER_PARENT_URL, FILE_MAP
import requests
import json
import os
from slugify import slugify
from zou.app.services import (
                                projects_service,
                            )
from .utils import with_app_context

@with_app_context
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
        project_data =  {'file_tree': file_tree, 'data': {'file_map': FILE_MAP, 'svn_url': svn_url}, 'file_name': project_file_name}
        projects_service.update_project(project_id, project_data)
    else:
        file_tree_dir = os.path.join(os.path.dirname(__file__), 'eaxum.json')
        with open(file_tree_dir, 'r') as f:
            file_tree = json.load(f)
        project_data =  {'file_tree': file_tree, 'data': {'file_map': FILE_MAP, 'svn_repositories': {'default': svn_url}}, 'file_name': project_file_name}
        projects_service.update_project(project_id, project_data)
    r = requests.post(url=f"{GENESIS_HOST}:{GENESIS_PORT}/project/{project_file_name}")
    print(r.status_code)