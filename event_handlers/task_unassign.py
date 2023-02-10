from .config import GENESIS_HOST, GENESIS_PORT
import requests
import os
from slugify import slugify
from zou.app.services import (
                                file_tree_service,
                                persons_service,
                                projects_service,
                                tasks_service,
                                entities_service
                            )
from .utils import get_base_file_directory, get_svn_base_directory, get_full_task
from zou.app.models.entity import Entity

def handle_event(data):
    project_id = data['project_id']
    project = projects_service.get_project(project_id)
    person_id = data['person_id']
    person = persons_service.get_person(person_id)
    task_id = data['task_id']
    # task = tasks_service.get_task(task_id)
    task = get_full_task(data['task_id'])

    project_name = slugify(project['name'], separator="_")

    entity = entities_service.get_entity_raw(task['entity_id'])
    file_extension = 'blend'
    task_type = tasks_service.get_task_type(str(task['task_type_id']))
    task_type_name = slugify(task_type['name'], separator='_')

    project_name = project['name'].replace(' ', '_').lower()
    working_file_path = file_tree_service.get_working_file_path(task)

    production_type = task['project']['production_type']
    if task_type_name in {'Editing', 'Edit', 'editing', 'edit'}:
        dependencies = []
        if production_type != 'tvshow':
            base_file_directory = os.path.join(project['file_tree']['working']['mountpoint'], \
                project['file_tree']['working']['root'],project_name,'edit','edit.blend')
        else:
            episode_name = slugify(task['episode']['name'], separator="_")
            base_file_directory = os.path.join(project['file_tree']['working']['mountpoint'], \
                project['file_tree']['working']['root'],project_name,'edit',f"{episode_name}_edit.blend")
    else:
        dependencies = Entity.serialize_list(entity.entities_out, obj_type="Asset")
        base_file_directory = get_base_file_directory(project, working_file_path, task_type_name, file_extension)

    if base_file_directory:
        base_svn_directory = get_svn_base_directory(project, base_file_directory)
        dependencies_payload = list()
        for dependency in dependencies:
            task_id = tasks_service.get_tasks_for_asset(dependency['id'])[0]
            dependency_working_file_path = file_tree_service.get_working_file_path(task_id)
            dependency_base_file_directory = get_base_file_directory(project, dependency_working_file_path, 'base', file_extension)
            dependency_base_svn_directory = get_svn_base_directory(project, dependency_base_file_directory)
            dependencies_payload.append(dependency_base_svn_directory)

        project_shot_task_types = {slugify(i['name'], separator='_') for i in tasks_service.get_task_types_for_project(project_id) if i['for_entity']=="Shot"}
        if task_type_name in project_shot_task_types:
            for shot_task_type in project_shot_task_types:
                if task_type_name != shot_task_type:
                    task_type_map = shot_task_type
                    dependency_working_file_path = file_tree_service.get_working_file_path(task)
                    dependency_base_file_directory = get_base_file_directory(project, dependency_working_file_path, task_type_map, file_extension)
                    if dependency_base_file_directory:
                        dependency_base_svn_directory = get_svn_base_directory(project, dependency_base_file_directory)
                        dependencies_payload.append(dependency_base_svn_directory)

        project_asset_task_types = {slugify(i['name'], separator='_') for i in tasks_service.get_task_types_for_project(project_id) if i['for_entity']=="Asset"}
        if task_type_name in project_asset_task_types:
            for asset_task_type in project_asset_task_types:
                if task_type_name != asset_task_type:
                    task_type_map = asset_task_type
                    dependency_working_file_path = file_tree_service.get_working_file_path(task)
                    dependency_base_file_directory = get_base_file_directory(project, dependency_working_file_path, task_type_map, file_extension)
                    if dependency_base_file_directory:
                        dependency_base_svn_directory = get_svn_base_directory(project, dependency_base_file_directory)
                        dependencies_payload.append(dependency_base_svn_directory)
        payload = {
            'task': task,
            'base_svn_directory':base_svn_directory,
            "task_type":task_type['name'].lower(),
            'person':person,
            'permission': 'none',
            'dependencies': dependencies_payload,
            'main_file_name': os.path.basename(working_file_path),
        }
        requests.put(url=f"{GENESIS_HOST}:{GENESIS_PORT}/task_acl/{project_name}", json=payload)