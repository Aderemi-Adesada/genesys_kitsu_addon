import json
import os
from slugify import slugify
from .config import GENESIS_HOST, GENESIS_PORT
import requests
from zou.app.services import (
                                shots_service,
                                entities_service,
                            )
from zou.app.models.entity import Entity
from .utils import update_shot_data

def handle_event(data):
    print('---------------------SHOT DEP UPDATE--------------------------')
    print(data)
    shot_id = data['shot_id']
    shot = shots_service.get_shot(shot_id)
    entity = entities_service.get_entity_raw(shot_id)
    dependencies = Entity.serialize_list(entity.entities_out, obj_type="Asset")
    print(dependencies)
    # entity_links
    payload = {
        "entity_in_id": shot_id,
        "entity_out_id": dependencies[0]['id'],
        "nb_occurences": genesys_project_id,
    }
    requests.post(url=f"{GENESIS_HOST}:{GENESIS_PORT}/data/entity_links", json=payload, timeout=5)
    print('----------------------SHOT DEP UPDATE END-------------------')