import os
GENESIS_HOST = os.getenv("GENESIS_HOST", "http://127.0.0.1")
GENESIS_PORT = os.getenv("GENESIS_PORT", 5002)
SVN_SERVER_PARENT_URL = os.getenv("SVN_SERVER_PARENT_URL", "http://localhost/svn")
FILE_MAP = {
            'concept':'none',
            'storyboard':'none',
            'staging':'base',
            'modeling':'modeling',
            'rigging':'rigging',
            'shading':'shading',
            'grooming':'grooming',
            'layout':'layout',
            'previz':'layout',
            'animation':'anim',
            'lighting':'lighting',
            'fx':'fx',
            'rendering':'lighting',
            'compositing':'comp',
        }