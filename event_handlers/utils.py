import os
from .config import FILE_MAP, USE_ROCKET_CHAT_BOT, RC_SERVER_URL, RC_USER, RC_USER_TOKEN
from functools import wraps
from zou.app.services import (
                                projects_service,
                                tasks_service,
                                file_tree_service,
                                assets_service,
                                shots_service,
                                entities_service,
                                persons_service,

                            )
from zou.app.utils import cache
from zou.app.services.exception import PersonNotFoundException
from slugify import slugify
from zou.app import app
from .rocketchat.rocketchat import RocketChat
from requests import sessions

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
    return base_svn_directory.lower()

def get_base_file_directory(project, working_file_path, task_type_name, file_extension):
    if task_type_name == 'base':
        return f'{working_file_path}.{file_extension}'
    project_id = project['id']
    project_file_map = project['data'].get('file_map')
    if project_file_map == None:
        update_project_data(project_id, {'file_map': FILE_MAP})
        project_file_map = FILE_MAP
    task_type_map = project_file_map.get(task_type_name)
    if task_type_map == 'base':
        return f'{working_file_path}.{file_extension}'
    elif task_type_map == 'none':
        return None
    elif task_type_map == None:
        update_file_map(project_id, {task_type_name:task_type_name})
        return f'{working_file_path}_{task_type_name}.{file_extension}'
    else:
        return f'{working_file_path}_{task_type_map}.{file_extension}'

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
    print('00000000000000000000000000000000000000000000000000000000000000000000000000')
    print(USE_ROCKET_CHAT_BOT)
    print(RC_SERVER_URL)
    print(RC_USER)
    print(RC_USER_TOKEN)
    print('00000000000000000000000000000000000000000000000000000000000000000000000000')
    if USE_ROCKET_CHAT_BOT:
        token = RC_USER_TOKEN
        user = RC_USER
        server_url=RC_SERVER_URL
        def get_user(users, username):
            for user in users:
                if 'username' in user.keys() and username == user['username']:
                    return user
            return None
        with sessions.Session() as session:
            rocket = RocketChat(user=user, auth_token=token, server_url=server_url)
            user = get_user(rocket.users_list().json()['users'], recipient)
            if user:
                user_id = user['_id']
                rocket.chat_post_message(message, channel=user_id)