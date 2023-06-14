from .config import GENESIS_HOST, GENESIS_PORT
import requests
import json
import os
from slugify import slugify
from zou.app.services import (
                                projects_service,
                                edits_service,
                            )
from .utils import rename_task_file, update_edit_data

def handle_event(data):
    project_id = data['project_id']
    edit_id = data['edit_id']
    project = projects_service.get_project(project_id)

    edit = edits_service.get_edit(edit_id)
    edit_name = edit['name']
    edit_file_name = slugify(edit_name, separator="_")
    project_name = slugify(project['name'], separator='_')

    if 'file_name' in edit['data'].keys():
        old_edit_file_name = edit['data']['file_name']
    else:
        edit_info = {'file_name': edit_file_name}
        update_edit_data(edit_id, edit_info)
        old_edit_file_name = edit_file_name

    if old_edit_file_name != edit_file_name:
        payload = {"name": edit_name,"secondary_id": edit_id}
        requests.put(url=f"{GENESIS_HOST}:{GENESIS_PORT}/data/entities", json=payload, timeout=5)

        edit_info = {'file_name': edit_file_name}
        update_edit_data(edit_id, edit_info)