# import requests
import json
import os
from slugify import slugify
from zou.app.services import (
                                assets_service,
                            )
from .utils import update_asset_data

def handle_event(data):
    project_id = data['project_id']
    asset_id = data['asset_id']
    asset = assets_service.get_asset(asset_id)
    asset_name = asset['name']
    asset_file_name = slugify(asset_name, separator="_")

    asset_info = {'file_name': asset_file_name}
    update_asset_data(asset_id, asset_info)