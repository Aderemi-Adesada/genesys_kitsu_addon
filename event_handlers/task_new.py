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
from .utils import get_base_file_directory, get_svn_base_directory, get_full_task, with_app_context

@with_app_context
def handle_event(data):
    project_id = data['project_id']
    project = projects_service.get_project(project_id)

    project_name = project['name']
    project_file_name = slugify(project_name, separator="_")

    # task = tasks_service.get_task(data['task_id'])
    task = get_full_task(data['task_id'])
    task_type = tasks_service.get_task_type(task['task_type_id'])
    task_type_name = task_type['name'].lower()
    working_file_path = file_tree_service.get_working_file_path(task)
    # is_asset = assets_service.is_asset(entity)
    for_entity = task["task_type"]["for_entity"]
    main_file_name = os.path.basename(working_file_path)

    all_persons = persons_service.get_persons()
    production_type = task['project']['production_type']
    if task_type_name.lower() in {'editing', 'edit'}:
        if production_type != 'tvshow':
            base_file_directories = [os.path.join(project['file_tree']['working']['mountpoint'], \
                project['file_tree']['working']['root'],project_file_name,'edit','edit.blend')]
        else:
            episode_name = slugify(task['episode']['name'], separator="_")
            base_file_directories = [os.path.join(project['file_tree']['working']['mountpoint'], \
                project['file_tree']['working']['root'],project_file_name,'edit',f"{episode_name}_edit.blend")]
    else:
        base_file_directories = get_base_file_directory(project, working_file_path, task_type_name)
    if base_file_directories:
        for base_file_directory in base_file_directories:
            file_name = os.path.basename(base_file_directory).rsplit('.', 1)[0]
            file_acl_path = get_svn_base_directory(project, base_file_directory)
            if for_entity.lower() == "asset":
                base_file_maps_directory = os.path.join(os.path.dirname(base_file_directory), 'maps', main_file_name)
                file_maps_acl_path = os.path.join(os.path.dirname(file_acl_path), 'maps', main_file_name)
                collection_name = main_file_name

            else:
                base_file_maps_directory = os.path.join(os.path.dirname(base_file_directory), 'maps', file_name)
                file_maps_acl_path = os.path.join(os.path.dirname(file_acl_path), 'maps', file_name)
                collection_name = file_name

            root = os.path.join(project['file_tree']['working']['mountpoint'], project['file_tree']['working']['root'],'')
            # replacing file tree mount point with genesys config mount point
            base_file_directory = base_file_directory.split(root,1)[1]

            payload = {
                    "base_file_directory":base_file_directory,
                    "base_file_map_directory":base_file_maps_directory,
                    "file_acl_path":file_acl_path,
                    "file_maps_acl_path":file_maps_acl_path,
                    "collection_name":collection_name,
            }
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