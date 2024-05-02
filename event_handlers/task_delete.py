from .config import GENESIS_HOST, GENESIS_PORT, SVN_SERVER_PARENT_URL, FILE_MAP
import requests
import json
import os
from slugify import slugify
from flask import current_app
from zou import app
from zou.app.services import (
                                file_tree_service,
                                persons_service,
                                projects_service,
                                assets_service,
                                tasks_service,
                                shots_service,
                                entities_service
                            )

def handle_event(data):
    print(data)