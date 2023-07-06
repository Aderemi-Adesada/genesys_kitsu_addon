import json
import os
from zou.app.services import (
                                persons_service,
                                tasks_service,
                            )
from .config import LOGIN_NAME
from .utils import send_status_notification, get_full_task, with_app_context

@with_app_context
def handle_event(data):
    all_persons = persons_service.get_persons()
    task = get_full_task(data['task_id'])
    task_departmet_id = task['task_type']['department_id']

    new_task_status_id = data['new_task_status_id']
    previous_task_status_id = data['previous_task_status_id']
    new_status_name = tasks_service.get_task_status(new_task_status_id)['name']
    previous_status_name = tasks_service.get_task_status(previous_task_status_id)['name']

    person_id = data['person_id']
    author_name = persons_service.get_person(person_id)['full_name']

    processed = []
    for person in task['persons']:
        if person[LOGIN_NAME] not in processed and not author_name == person['full_name']:
            processed.append(person[LOGIN_NAME])
            send_status_notification(person[LOGIN_NAME], task, previous_status_name, new_status_name, author_name)
    
    for person in all_persons:
        departments = person['departments']
        if person[LOGIN_NAME] not in processed and not author_name == person['full_name']:
            role = person['role']
            if role in {'manager'}:
                send_status_notification(person[LOGIN_NAME], task, previous_status_name, new_status_name, author_name)
            elif task_departmet_id in departments:
                if role in {'supervisor'}:
                    send_status_notification(person[LOGIN_NAME], task, previous_status_name, new_status_name, author_name)
