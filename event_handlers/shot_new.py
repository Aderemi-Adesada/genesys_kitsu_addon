import json
import os
from slugify import slugify
from zou.app.services import (
                                shots_service,
                            )


def handle_event(data):
    project_id = data['project_id']
    shot_id = data['shot_id']

    shot = shots_service.get_shot(shot_id)
    shot_name = shot['name']
    shot_file_name = slugify(shot_name, separator="_")

    data_dir = os.path.join(os.path.dirname(__file__), 'data.json')
    with open(data_dir) as file:
        genesys_data = json.load(file)

    try:
        genesys_project_data = genesys_data[project_id]
        genesys_project_data['shots'][shot_id] = {'file_name': shot_file_name}
        with open(data_dir, 'w') as file:
            json.dump(genesys_data, file, indent=2)
    except KeyError:
        print("Project not found in genesys")