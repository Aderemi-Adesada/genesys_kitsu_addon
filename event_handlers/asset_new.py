# import requests
import json
import os
from slugify import slugify
from zou.app.services import (
                                assets_service,
                            )


def handle_event(data):
    project_id = data['project_id']
    asset_id = data['asset_id']
    asset = assets_service.get_asset(asset_id)
    asset_name = asset['name']
    asset_file_name = slugify(asset_name, separator="_")

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