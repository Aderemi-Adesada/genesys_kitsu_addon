import json
import os
from slugify import slugify
from zou.app.services import (
                                shots_service,
                            )
from .utils import update_shot_data

def handle_event(data):
    project_id = data['project_id']
    shot_id = data['shot_id']

    shot = shots_service.get_shot(shot_id)
    shot_name = shot['name']
    shot_file_name = slugify(shot_name, separator="_")

    asset_info = {'file_name': shot_file_name}
    update_shot_data(shot_id, asset_info)