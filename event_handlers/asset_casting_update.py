import json
import os
from slugify import slugify
from .config import GENESIS_HOST, GENESIS_PORT
import requests
from zou.app.services import (
                                assets_service,
                                entities_service,
                            )
from .utils import update_shot_data
from zou.app.models.entity import Entity

def handle_event(data):
    print('------------------ASSET LINK-----------------------')
    print(data)
    asset_id = data['asset_id']
    asset = assets_service.get_asset(asset_id)
    entity = entities_service.get_entity_raw(asset_id)
    dependencies = Entity.serialize_list(entity.entities_out, obj_type="Asset")
    print(dependencies)
    print('---------------------ASSET LINK END--------------------------')