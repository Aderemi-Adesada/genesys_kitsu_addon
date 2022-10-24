import os
from .config import FILE_MAP
from zou.app.services import (
                                projects_service,
                                tasks_service,
                                file_tree_service,
                                assets_service,
                                shots_service,

                            )
from slugify import slugify

def update_file_map(project_id, data: dict):
    project = projects_service.get_project(project_id)
    project_data = project['data']
    project_data['file_map'].update(data)
    new_project_data = {'data': project_data}
    projects_service.update_project(project_id, new_project_data)

def update_project_data(project_id, data: dict):
    project = projects_service.get_project(project_id)
    project_data = project['data']
    project_data.update(data)
    updated_project_data = {'data': project_data}

    project_raw = projects_service.get_project_raw(project_id)
    project_raw.update(updated_project_data)

def update_asset_data(asset_id, data: dict):
    asset = assets_service.get_asset(asset_id)
    if asset['data'] == None:
        asset['data'] = {}
    asset_data = asset['data']
    asset_data.update(data)
    updated_asset_data = {'data': asset_data}

    asset_raw = assets_service.get_asset_raw(asset_id)
    asset_raw.update(updated_asset_data)

def update_shot_data(shot_id, data: dict):
    shot = shots_service.get_shot(shot_id)
    if shot['data'] == None:
        shot['data'] = {}
    shot_data = shot['data']
    shot_data.update(data)
    updated_shot_data = {'data': shot_data}

    shot_raw = shots_service.get_shot_raw(shot_id)
    shot_raw.update(updated_shot_data)

def get_svn_base_directory(project:dict, base_file_directory):
    '''
        get svn repository acl directory
    '''
    project_file_name = slugify(project['name'], separator="_")
    root = os.path.join(project['file_tree']['working']['mountpoint'], project['file_tree']['working']['root'],project_file_name,'')
    # base_svn_directory = os.path.join(f"{project['name']}:",base_file_directory.split(root.lower(),1)[1])
    base_svn_directory = os.path.join(f"{project_file_name}:",base_file_directory.split(root.lower(),1)[1])
    return base_svn_directory.lower()

def get_base_file_directory(project, working_file_path, task_type_name, file_extension):
    project_id = project['id']
    project_file_map = project['data'].get('file_map')
    if project_file_map == None:
        update_project_data(project_id, {'file_map': FILE_MAP})
        project_file_map = FILE_MAP
    task_type_map = project_file_map.get(task_type_name)
    if task_type_map == 'base':
        base_file_directory = f'{working_file_path}.{file_extension}'
    elif task_type_map == 'none':
        base_file_directory = None
    elif task_type_map == None:
        update_file_map(project_id, {task_type_name:task_type_name})
        base_file_directory = f'{working_file_path}_{task_type_name}.{file_extension}'
    else:
        base_file_directory = f'{working_file_path}_{task_type_map}.{file_extension}'
    return base_file_directory

def rename_task_file(new_name, old_name, task, project, payload, entity_type):
    tasks_service.clear_task_cache(task['id'])
    task_type = tasks_service.get_task_type(task['task_type_id'])
    task_type_name = task_type['name'].lower()
    file_extension = 'blend'
    # FIXME working file path different from new entity name when task is renamed

    if entity_type == 'asset':
        # set working file path to previous name
        working_file_path = file_tree_service.get_working_file_path(task) \
            .rsplit('/', 1)
        working_file_path = os.path.join(working_file_path[0], old_name)
        new_file_name = new_name
        new_working_file_path = os.path.join(os.path.dirname(working_file_path), new_file_name)
    elif entity_type == 'shot':
        working_file_path = file_tree_service.get_working_file_path(task) \
            .rsplit('/', 2)
        shot_file_name = f"{working_file_path[2].rsplit('_', 1)[0]}_{old_name}"
        new_file_name = f"{working_file_path[2].rsplit('_', 1)[0]}_{new_name}"
        working_file_path = os.path.join(working_file_path[0],old_name,shot_file_name)
        shot_folder = os.path.join(os.path.dirname(os.path.dirname(working_file_path)), \
            new_file_name.rsplit('_', 1)[1])
        new_working_file_path = os.path.join(shot_folder, new_file_name)
    base_file_directory = get_base_file_directory(project, working_file_path, task_type_name, file_extension)
    new_base_file_directory = get_base_file_directory(project, new_working_file_path, task_type_name, file_extension)
    if base_file_directory:
        base_svn_directory = get_svn_base_directory(project, base_file_directory)
        new_base_svn_directory = get_svn_base_directory(project, new_base_file_directory)
        task_payload = {
            'entity_type':entity_type,
            'project':project,
            'base_svn_directory':base_svn_directory,
            'new_base_svn_directory':new_base_svn_directory,
            'base_file_directory':base_file_directory,
            'new_base_file_directory':new_base_file_directory,
            'task_type':task_type_name,
        }
        payload.append(task_payload)
