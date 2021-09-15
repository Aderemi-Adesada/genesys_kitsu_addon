from .config import GENESIS_HOST, GENESIS_PORT
import requests
from slugify import slugify
from zou.app.services import (
                                file_tree_service,
                                persons_service,
                                projects_service,
                                tasks_service,
                                entities_service
                            )
from .utils import get_base_file_directory, get_svn_base_directory
from zou.app.models.entity import Entity

def handle_event(data):
    project_id = data['project_id']
    project = projects_service.get_project(project_id)
    person_id = data['person_id']
    person = persons_service.get_person(person_id)
    task_id = data['task_id']
    task = tasks_service.get_task(task_id)

    project_name = slugify(project['name'], separator="_")

    entity = entities_service.get_entity_raw(task['entity_id'])
    file_extension = 'blend'
    task_type = tasks_service.get_task_type(str(task['task_type_id']))
    task_type_name = task_type['name'].lower()
    dependencies = Entity.serialize_list(entity.entities_out, obj_type="Asset")

    project_name = project['name'].replace(' ', '_').lower()
    working_file_path = file_tree_service.get_working_file_path(task)
    base_file_directory = get_base_file_directory(project, working_file_path, task_type_name, file_extension)
    if base_file_directory:
        base_svn_directory = get_svn_base_directory(project, base_file_directory)
        dependencies_payload = list()
        for dependency in dependencies:
            task_id = tasks_service.get_tasks_for_asset(dependency['id'])[0]
            dependency_working_file_path = file_tree_service.get_working_file_path(task_id)
            dependency_base_file_directory = get_base_file_directory(project, dependency_working_file_path, 'modeling', file_extension)
            dependency_base_svn_directory = get_svn_base_directory(project, dependency_base_file_directory)
            dependencies_payload.append(dependency_base_svn_directory)
        payload = {
            'base_svn_directory':base_svn_directory,
            "task_type":task_type['name'].lower(),
            'person':person,
            'permission': 'none',
            'dependencies': dependencies_payload,
        }
        requests.put(url=f"{GENESIS_HOST}:{GENESIS_PORT}/task_acl/{project_name}", json=payload)