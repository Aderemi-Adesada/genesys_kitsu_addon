from gazu.project import new_project
from .config import GENESIS_HOST, GENESIS_PORT, SVN_SERVER_PARENT_URL, FILE_MAP
import requests
import gazu
import json
import os
from slugify import slugify
from flask import current_app
from zou import app
from zou.app.services import (
                                file_tree_service,
                                persons_service,
                                projects_service,
                                assets_service,
                                tasks_service,
                                shots_service,
                                entities_service
                            )
from .utils import get_base_file_directory, get_svn_base_directory


def handle_event(data):
    project_id = data['project_id']
    project = projects_service.get_project(project_id)

    project_name = project['name']
    project_file_name = slugify(project_name, separator="_")
    svn_url = os.path.join(SVN_SERVER_PARENT_URL, project_file_name)

    data_dir = os.path.join(os.path.dirname(__file__), 'data.json')
    with open(data_dir) as file:
        genesys_data = json.load(file)

    task = tasks_service.get_task(data['task_id'])
    task_type = tasks_service.get_task_type(task['task_type_id'])
    task_type_name = task_type['name'].lower()
    file_extension = 'blend'
    working_file_path = file_tree_service.get_working_file_path(task)


    all_persons = persons_service.get_persons()
    base_file_directory = get_base_file_directory(project, working_file_path, task_type_name, file_extension)
    if base_file_directory:
        base_svn_directory = get_svn_base_directory(project, base_file_directory)
        payload = {
                "project":project,
                "base_file_directory":base_file_directory,
                "base_svn_directory":base_svn_directory,
                "all_persons":all_persons,
                "task_type":task_type_name
        }
        # requests.post(url=f"{GENESIS_HOST}:{GENESIS_PORT}/task/{project_file_name}", json=payload)

    














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