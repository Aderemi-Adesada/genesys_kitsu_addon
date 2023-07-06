import json
import os
from slugify import slugify
from zou.app.services import (
                                persons_service,
                                tasks_service,
                                comments_service,
                            )
from .config import LOGIN_NAME
from .utils import send_comment_notification, with_app_context

@with_app_context
def handle_event(data):
    comment_id = data['comment_id']
    all_persons = persons_service.get_persons()
    task = tasks_service.get_full_task(data['task_id'])
    task_departmet_id = task['task_type']['department_id']
    comment = tasks_service.get_comment_raw(comment_id).serialize()
    text = comment['text']
    if text:
        mentions = [i.serialize() for i in comments_service.get_comment_mentions(data['task_id'], text)]

        person_id = comment['person_id']
        author_name = persons_service.get_person(person_id)['full_name']

        processed = []
        for person in task['persons']:
            if person[LOGIN_NAME] not in processed and not author_name == person['full_name']:
                processed.append(person[LOGIN_NAME])
                send_comment_notification(person[LOGIN_NAME], task, text, author_name)
        
        for person in mentions:
            if person[LOGIN_NAME] not in processed and not author_name == person['full_name']:
                processed.append(person[LOGIN_NAME])
                send_comment_notification(person[LOGIN_NAME], task, text, author_name)
        
        for person in all_persons:
            departments = person['departments']
            if person[LOGIN_NAME] not in processed and not author_name == person['full_name']:
                role = person['role']
                if role in {'manager'}:
                    send_comment_notification(person[LOGIN_NAME], task, text, author_name)
                elif task_departmet_id in departments:
                    if role in {'supervisor'}:
                        send_comment_notification(person[LOGIN_NAME], task, text, author_name)
