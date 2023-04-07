import os
GENESIS_HOST = os.getenv("GENESIS_HOST", "http://127.0.0.1")
GENESIS_PORT = os.getenv("GENESIS_PORT", 5002)
SVN_SERVER_PARENT_URL = os.getenv("SVN_SERVER_PARENT_URL", "http://localhost/svn")
blender = {
            'name': 'blender',
            'extension': 'blend',
            'use_default': True,
            'alternate': 'none'
        }
clipstudio = {
            'name': 'clipstudio',
            'extension': 'clip',
            'use_default': True,
            'alternate': 'none'
        }
sketchbook = {
            'name': 'sketchbook',
            'extension': 'tif',
            'use_default': True,
            'alternate': 'none'
        }
flstudio = {
            'name': 'flstudio',
            'extension': 'flp',
            'use_default': True,
            'alternate': 'none'
        }
mixer = {
            'name': 'mixer',
            'extension': 'folder',
            'use_default': True,
            'alternate': 'none'
        }
maya = {
            'name': 'maya',
            'extension': 'ma',
            'use_default': True,
            'alternate': 'none'
        }
FILE_MAP = {
    'concept': {
        'file': 'base',
        'softwares': [sketchbook]
    },
    'storyboard': {
        'file': 'base',
        'softwares': [clipstudio]
    },
    'staging': {
        'file': 'base',
        'softwares': [blender]
    },
    'modeling': {
        'file': 'modeling',
        'softwares': [blender]
    },
    'rigging': {
        'file': 'rigging',
        'softwares': [blender]
    },
    'shading': {
        'file': 'shading',
        'softwares': [blender]
    },
    'grooming': {
        'file': 'grooming',
        'softwares': [blender]
    },
    'layout': {
        'file': 'layout',
        'softwares': [blender]
    },
    'previz': {
        'file': 'layout',
        'softwares': [blender]
    },
    'animation': {
        'file': 'anim',
        'softwares': [blender]
    },
    'lighting': {
        'file': 'lighting',
        'softwares': [blender]
    },
    'fx': {
        'file': 'fx',
        'softwares': [blender]
    },
    'rendering': {
        'file': 'lighting',
        'softwares': [blender]
    },
    'compositing': {
        'file': 'comp',
        'softwares': [blender]
    },
    'sound': {
        'file': 'sound',
        'softwares': [flstudio]
    },
}

LOGIN_NAME = os.getenv("LOGIN_NAME", "email")
USE_ROCKET_CHAT_BOT = os.getenv("USE_ROCKET_CHAT_BOT", "False").lower() == "true"
RC_USER = os.getenv("RC_USER", None)
RC_USER_PASSWORD = os.getenv("RC_USER_PASSWORD", None)
# RC_USER_TOKEN = os.getenv("RC_USER_TOKEN", None)
RC_SERVER_URL = os.getenv("RC_SERVER_URL", None)
