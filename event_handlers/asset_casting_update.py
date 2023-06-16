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

def handle_event(data):
    print('------------------ASSET LINK-----------------------')
    print(data)
    asset_id = data['asset_id']
    asset = assets_service.get_asset(asset_id)
    entity = entities_service.get_entity(asset_id)
    print(asset)
    print("###############################################")
    print(entity)
    print('---------------------ASSET LINK END--------------------------')