from .config import GENESIS_HOST, GENESIS_PORT
import requests
import os
from slugify import slugify
from zou.app.services import (
                                file_tree_service,
                                persons_service,
                                projects_service,
                                tasks_service,
                            )
from .utils import get_base_file_directory, get_svn_base_directory


def handle_event(data):
    project_id = data['project_id']
    project = projects_service.get_project(project_id)

    project_name = project['name']
    project_file_name = slugify(project_name, separator="_")

    task = tasks_service.get_task(data['task_id'])
    task_type = tasks_service.get_task_type(task['task_type_id'])
    task_type_name = task_type['name'].lower()
    file_extension = 'blend'
    working_file_path = file_tree_service.get_working_file_path(task)


    all_persons = persons_service.get_persons()
    if task_type_name in {'Editing', 'Edit', 'editing', 'edit'}:
        if task['episode_name'] == None:
            base_file_directory = os.path.join(project['file_tree']['working']['mountpoint'], \
                project['file_tree']['working']['root'],project_file_name,'edit','edit.blend')
        else:
            base_file_directory = os.path.join(project['file_tree']['working']['mountpoint'], \
                project['file_tree']['working']['root'],project_file_name,'edit',f"{task['episode_name']}_edit.blend")
    else:
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
        print(payload)
        requests.post(url=f"{GENESIS_HOST}:{GENESIS_PORT}/task/{project_file_name}", json=payload)

    














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