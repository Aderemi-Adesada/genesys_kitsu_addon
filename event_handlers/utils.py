import os
from .config import FILE_MAP, USE_ROCKET_CHAT_BOT, RC_SERVER_URL, RC_USER, RC_USER_PASSWORD
from functools import wraps
from zou.app.services import (
                                projects_service,
                                tasks_service,
                                file_tree_service,
                                assets_service,
                                shots_service,
                                entities_service,
                                persons_service,
                                emails_service,

                            )
from zou.app.utils import cache
from zou.app.services.exception import PersonNotFoundException
from slugify import slugify
from zou.app import app
from .rocketchat import RocketChat
from requests import sessions
import requests
from .config import GENESIS_PORT, GENESIS_HOST, LOGIN_NAME
from zou.app.models.entity import Entity

def with_app_context(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with app.app_context():
            return func(*args, **kwargs)
    return wrapper

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
    return base_svn_directory

def get_base_file_directory(project, working_file_path, task_type_name):
    if task_type_name == 'base':
        return [f"{working_file_path}.blend"]
    project_id = project['id']
    project_file_map = project['data'].get('file_map')
    if project_file_map == None:
        update_project_data(project_id, {'file_map': FILE_MAP})
        project_file_map = FILE_MAP
    task_type_map = project_file_map.get(task_type_name)
    if task_type_map == None:
        new_file_map = {task_type_name:{
            'file': task_type_name,
            'softwares': [{'name': 'blender','extension': 'blend','use_default': True,'alternate': 'none'}]
        }}
        update_file_map(project_id, new_file_map)
        return [f"{working_file_path}_{task_type_name}.{'blend'}"]
    elif task_type_map['file'] == 'base':
        working_files = []
        for sofware in task_type_map['softwares']:
            working_file = f"{working_file_path}.{sofware['extension']}"
            working_files.append(working_file)
        return working_files
    elif task_type_map['file'] == 'none':
        return None
    else:
        working_files = []
        for sofware in task_type_map['softwares']:
            working_file = f"{working_file_path}_{task_type_map['file']}.{sofware['extension']}"
            working_files.append(working_file)
        return working_files

def rename_task_file(new_name, old_name, task, project, payload, entity_type):
    tasks_service.clear_task_cache(task['id'])
    task_type = tasks_service.get_task_type(task['task_type_id'])
    task_type_name = task_type['name'].lower()
    # FIXME working file path different from new entity name when task is renamed
    root = os.path.join(project['file_tree']['working']['mountpoint'], project['file_tree']['working']['root'], '')

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
    base_file_directory = get_base_file_directory(project, working_file_path, task_type_name)
    new_base_file_directory = get_base_file_directory(project, new_working_file_path, task_type_name)
    if base_file_directory:
        acl_path = get_svn_base_directory(project, base_file_directory)
        new_acl_path = get_svn_base_directory(project, new_base_file_directory)

        # replacing file tree mount point with genesys config mount point
        base_file_directory = base_file_directory.split(root,1)[1]
        new_base_file_directory = new_base_file_directory.split(root,1)[1]
        task_payload = {
            'acl_path':acl_path,
            'new_acl_path':new_acl_path,
            'base_file_directory':base_file_directory,
            'new_base_file_directory':new_base_file_directory,
        }
        payload.append(task_payload)

@cache.memoize_function(120)
def get_full_task(task_id):
    task = tasks_service.get_task_with_relations(task_id)
    task_type = tasks_service.get_task_type(task["task_type_id"])
    project = projects_service.get_project(task["project_id"])
    task_status = tasks_service.get_task_status(task["task_status_id"])
    entity = entities_service.get_entity(task["entity_id"])
    entity_type = entities_service.get_entity_type(entity["entity_type_id"])
    assignees = [
        persons_service.get_person(assignee_id)
        for assignee_id in task["assignees"]
    ]

    task.update(
        {
            "entity": entity,
            "entity_type": entity_type,
            "persons": assignees,
            "project": project,
            "task_status": task_status,
            "task_type": task_type,
            "type": "Task",
        }
    )

    try:
        assigner = persons_service.get_person(task["assigner_id"])
        task["assigner"] = assigner
    except PersonNotFoundException:
        pass

    if entity["parent_id"] is not None:
        if entity_type["name"] not in ["Asset", "Shot"]:
            episode_id = entity["parent_id"]
        else:
            sequence = shots_service.get_sequence(entity["parent_id"])
            task["sequence"] = sequence
            episode_id = sequence["parent_id"]
        if episode_id is not None:
            episode = shots_service.get_episode(episode_id)
            task["episode"] = episode

    return task

def send_message_to_rc(message, recipient):
    if USE_ROCKET_CHAT_BOT:
        try:
            def get_user(users, username):
                for user in users:
                    if 'username' in user.keys() and username == user['username']:
                        return user
                return None
            with sessions.Session() as session:
                rocket = RocketChat(user=RC_USER, password=RC_USER_PASSWORD, server_url=RC_SERVER_URL)
                user = get_user(rocket.users_list().json()['users'], recipient)
                if user:
                    user_id = user['_id']
                    rocket.chat_post_message(message, channel=user_id)
        except Exception as e:
            print('Failed to send message to rocket chat')
            print(e)


def send_assignation_notification(person_login_name, task):
    """
    Send a notification email telling that somenone assigned to a task the
    person matching given person id.
    """
    (author, task_name, task_url) = emails_service.get_task_descriptors(task['assigner_id'], task)
    author_full_name = author["full_name"]
    message = f":kitsu: *{author_full_name}* assigned you to <{task_url}|{task_name}>."
    send_message_to_rc(message, person_login_name)

def send_status_notification(person_login_name, task, previous_status_name, new_status_name, author_name):
    (author, task_name, task_url) = emails_service.get_task_descriptors(task['assigner_id'], task)
    message = f":kitsu: *{author_name}* changed status of <{task_url}|{task_name}> from *{previous_status_name}* to *{new_status_name}*."
    send_message_to_rc(message, person_login_name)

def send_comment_notification(person_login_name, task, text, author_name):
    (author, task_name, task_url) = emails_service.get_task_descriptors(task['assigner_id'], task)
    message = f':kitsu: *{author_name}* made a comment on <{task_url}|{task_name}> - "{text}".'
    send_message_to_rc(message, person_login_name)

def set_acl(task, person, permission, task_type, acl_path, dependencies, project, working_file_path):
    acl_paths = []
    acl_paths.append(acl_path)
    for_entity = task["task_type"]["for_entity"]
    main_file_name = os.path.basename(working_file_path)

    splited_file_map_folder_url = acl_path.split(':', 1)
    base_file_directory = f"{splited_file_map_folder_url[0]}{splited_file_map_folder_url[1]}"
    file_name = os.path.basename(base_file_directory).rsplit('.', 1)[0]

    if for_entity.lower() == "asset":
        base_map_svn_directory = os.path.join(os.path.dirname(acl_path), 'maps', main_file_name)
    else:
        base_map_svn_directory = os.path.join(os.path.dirname(acl_path), 'maps', file_name)

    project_name = slugify(project['name'], separator='_')
    project_id = project['id']
    task_type_name = slugify(task_type['name'], separator='_')
    acl_paths.append(base_map_svn_directory)
    # acl_paths.append(f"{base_map_svn_directory}/**")
    acl_paths_dependencies = list()
    for dependency in dependencies:
        task_id = tasks_service.get_tasks_for_asset(dependency['id'])[0]
        dependency_working_file_path = file_tree_service.get_working_file_path(task_id)
        dependency_base_file_directory = get_base_file_directory(project, dependency_working_file_path, 'base')[0]
        dependency_base_svn_directory = get_svn_base_directory(project, dependency_base_file_directory)
        acl_paths_dependencies.append(dependency_base_svn_directory)

        dependency_main_file_name = os.path.basename(dependency_working_file_path)
        dependency_base_map_svn_directory = os.path.join(os.path.dirname(dependency_base_svn_directory), 'maps', dependency_main_file_name)
        if task_type_name.lower() not in {'anim', 'animation', 'sound', 'storyboard', 'keying'}:
            acl_paths_dependencies.append(dependency_base_map_svn_directory)
            # acl_paths_dependencies.append(f"{dependency_base_map_svn_directory}/**")

        entity = entities_service.get_entity_raw(dependency['id'])
        dependencies_of_dependency = Entity.serialize_list(entity.entities_out, obj_type="Asset")
        for dependency_of_dependency in dependencies_of_dependency:
            dependency_of_dependency_task_id = tasks_service.get_tasks_for_asset(dependency_of_dependency['id'])[0]
            dependency_of_dependency_working_file_path = file_tree_service.get_working_file_path(dependency_of_dependency_task_id)
            dependency_of_dependency_base_file_directory = get_base_file_directory(project, dependency_of_dependency_working_file_path, 'base')[0]
            dependency_of_dependency_base_svn_directory = get_svn_base_directory(project, dependency_of_dependency_base_file_directory)
            acl_paths_dependencies.append(dependency_of_dependency_base_svn_directory)

            dependency_of_dependency_main_file_name = os.path.basename(dependency_of_dependency_working_file_path)
            dependency_of_dependency_base_map_svn_directory = os.path.join(os.path.dirname(dependency_of_dependency_base_svn_directory), 'maps', dependency_of_dependency_main_file_name)
            if task_type_name.lower() not in {'anim', 'animation', 'sound', 'storyboard', 'keying'}:
                acl_paths_dependencies.append(dependency_of_dependency_base_map_svn_directory)
                # acl_paths_dependencies.append(f"{dependency_of_dependency_base_map_svn_directory}/**")
    #TODO implement DRY
    project_shot_task_types = {slugify(i['name'], separator='_') for i in tasks_service.get_task_types_for_project(project_id) if i['for_entity']=="Shot"}
    if task_type_name in project_shot_task_types:
        if task_type_name.lower() not in {'anim', 'animation', 'sound', 'storyboard', 'keying'}:
            for shot_task_type in project_shot_task_types:
                if shot_task_type.lower() in {'sound', 'storyboard', 'keying'}:
                    continue
                if task_type_name != shot_task_type:
                    task_type_map = shot_task_type
                    dependency_working_file_path = file_tree_service.get_working_file_path(task)
                    dependency_base_file_directories = get_base_file_directory(project, dependency_working_file_path, task_type_map)
                    if dependency_base_file_directories:
                        for dependency_base_file_directory in dependency_base_file_directories:
                            dependency_base_svn_directory = get_svn_base_directory(project, dependency_base_file_directory)
                            acl_paths_dependencies.append(dependency_base_svn_directory)
    
    project_asset_task_types = {slugify(i['name'], separator='_') for i in tasks_service.get_task_types_for_project(project_id) if i['for_entity']=="Asset"}
    if task_type_name in project_asset_task_types:
        for asset_task_type in project_asset_task_types:
            if task_type_name != asset_task_type:
                task_type_map = asset_task_type
                dependency_working_file_path = file_tree_service.get_working_file_path(task)
                dependency_base_file_directories = get_base_file_directory(project, dependency_working_file_path, task_type_map)
                if dependency_base_file_directories:
                    for dependency_base_file_directory in dependency_base_file_directories:
                        dependency_base_svn_directory = get_svn_base_directory(project, dependency_base_file_directory)
                        acl_paths_dependencies.append(dependency_base_svn_directory)
    payload = {
        'acl_paths': acl_paths,
        'person':person[LOGIN_NAME],
        'permission': permission,
        'acl_paths_dependencies': acl_paths_dependencies,
    }
    requests.put(url=f"{GENESIS_HOST}:{GENESIS_PORT}/task_acl/{project_name}", json=payload)