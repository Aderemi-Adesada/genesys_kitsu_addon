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
from .utils import get_base_file_directory, get_svn_base_directory, get_full_task, set_acl, reset_acl, with_app_context
from zou.app.models.entity import Entity

@with_app_context
def handle_event(data):
    project_id = data['project_id']
    # project = projects_service.get_project(project_id)
    # person_id = data['person_id']
    # person = persons_service.get_person(person_id)
    # task_id = data['task_id']

    gensys_url = f"{GENESIS_HOST}:{GENESIS_PORT}"
    reset_acl(
        project_id,
        gensys_url,  
        use_ignore_list = True,
        )
    # task = tasks_service.get_task(task_id)
    # task = get_full_task(data['task_id'])

    # project_name = slugify(project['name'], separator="_")

    # entity = entities_service.get_entity_raw(task['entity_id'])
    # task_type = tasks_service.get_task_type(str(task['task_type_id']))
    # task_type_name = slugify(task_type['name'], separator='_')

    # project_name = project['name'].replace(' ', '_').lower()
    # working_file_path = file_tree_service.get_working_file_path(task)

    # production_type = task['project']['production_type']
    # if task_type_name in {'Editing', 'Edit', 'editing', 'edit'}:
    #     dependencies = []
    #     if production_type != 'tvshow':
    #         base_file_directory = os.path.join(project['file_tree']['working']['mountpoint'], \
    #             project['file_tree']['working']['root'],project_name,'edit','edit.blend')
    #     else:
    #         episode_name = slugify(task['episode']['name'], separator="_")
    #         base_file_directory = os.path.join(project['file_tree']['working']['mountpoint'], \
    #             project['file_tree']['working']['root'],project_name,'edit',f"{episode_name}_edit.blend")
    # else:
    #     dependencies = Entity.serialize_list(entity.entities_out, obj_type="Asset")
    #     base_file_directories = get_base_file_directory(project, working_file_path, task_type_name)
    # if base_file_directories:
    #     for base_file_directory in base_file_directories:
    #         acl_path = get_svn_base_directory(project, base_file_directory)
    #         set_acl(
    #             task=task,
    #             person=person,
    #             permission='none', 
    #             task_type=task_type,
    #             acl_path=acl_path,
    #             dependencies=dependencies,
    #             project=project,
    #             working_file_path=working_file_path)