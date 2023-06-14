from .config import GENESIS_HOST, GENESIS_PORT
import requests
import json
import os
from slugify import slugify
from zou.app.services import (
                                projects_service,
                                shots_service,
                            )
from .utils import update_sequence_data

def handle_event(data):
    project_id = data['project_id']
    sequence_id = data['sequence_id']
    project = projects_service.get_project(project_id)

    sequence = shots_service.get_sequence(sequence_id)
    sequence_name = sequence['name']
    sequence_file_name = slugify(sequence_name, separator="_")
    project_name = slugify(project['name'], separator='_')

    if 'file_name' in sequence['data'].keys():
        old_sequence_file_name = sequence['data']['file_name']
    else:
        sequence_info = {'file_name': sequence_file_name}
        update_sequence_data(sequence_id, sequence_info)
        old_sequence_file_name = sequence_file_name

    if old_sequence_file_name != sequence_file_name:
        payload = {"name": sequence_name,"secondary_id": sequence_id}
        requests.put(url=f"{GENESIS_HOST}:{GENESIS_PORT}/data/entities", json=payload, timeout=5)

        sequence_info = {'file_name': sequence_file_name}
        update_sequence_data(sequence_id, sequence_info)