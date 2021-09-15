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
    project_id = data['project_id']
    asset_id = data['asset_id']
    project = projects_service.get_project(project_id)

    project_name = project['name']
    project_file_name = slugify(project_name, separator="_")
    asset = assets_service.get_asset(asset_id)
    asset_name = asset['name']
    asset_file_name = slugify(asset_name, separator="_")
    print(asset)
    svn_url = os.path.join(SVN_SERVER_PARENT_URL, project_file_name)

    data_dir = os.path.join(os.path.dirname(__file__), 'data.json')
    with open(data_dir) as file:
        genesys_data = json.load(file)

    try:
        genesys_project_data = genesys_data[project_id]
        genesys_project_data['assets'][asset_id] = {'file_name': asset_file_name}
        with open(data_dir, 'w') as file:
            json.dump(genesys_data, file, indent=2)
    except KeyError:
        print("Project not found in genesys")