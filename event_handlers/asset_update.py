import requests
from .config import GENESIS_HOST, GENESIS_PORT
import json
import os
from slugify import slugify
from zou.app.services import (
                                projects_service,
                                assets_service,
                            )
from .utils import rename_task_file
from .utils import update_asset_data

def handle_event(data):
    project_id = data['project_id']
    asset_id = data['asset_id']
    project = projects_service.get_project(project_id)
    asset = assets_service.get_asset(asset_id)
    asset_name = asset['name']
    asset_file_name = slugify(asset_name, separator="_")

    if 'file_name' in asset['data'].keys():
        old_asset_file_name = asset['data']['file_name']
    else:
        asset_info = {'file_name': asset_file_name}
        update_asset_data(asset_id, asset_info)
        old_asset_file_name = asset_file_name

    if old_asset_file_name != asset_file_name:
        payload = {"name": asset_name,"secondary_id": asset_id}
        requests.put(url=f"{GENESIS_HOST}:{GENESIS_PORT}/data/entities", json=payload, timeout=5)
        asset_info = {'file_name': asset_file_name}
        update_asset_data(asset_id, asset_info)