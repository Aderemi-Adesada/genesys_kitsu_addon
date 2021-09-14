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


def handle_event(data):
    # print(file_tree_service.get_tree_from_file('default'))
    project_id = data['project_id']
    project = projects_service.get_project(project_id)

    project_name = project['name']
    project_file_name = slugify(project_name, separator="_")

    data_dir = os.path.join(os.path.dirname(__file__), 'data.json')
    with open(data_dir) as file:
        data = json.load(file)

    old_project_file_name = data[project_id]['project_file_name']


    try:
        if old_project_file_name != project_file_name:
            payload = {
                'old_project_name':old_project_file_name,
                'new_project_name':project_file_name
                }
            project_name = data['name']
            # requests.put(url=f"{GENESIS_HOST}:{GENESIS_PORT}/project/{project_name}", json=payload)

            data[project_id]['project_file_name'] = project_file_name
            with open(data_dir, 'w') as file:
                json.dump(data, file)
    except KeyError:
        pass