import json
import os
from slugify import slugify
from .config import GENESIS_HOST, GENESIS_PORT
import requests
from zou.app.services import (
                                shots_service,
                                entities_service,
                            )
from .utils import update_shot_data

def handle_event(data):
    print('-----------------NEW LINK---------------------------')
    print('----------------------------------------------------------')
    print(data)
    print('----------------------------------------------------------')
    print('----------------------------------------------------------')