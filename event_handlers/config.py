import os
ENABLE_GENESIS = os.getenv("ENABLE_GENESIS", "False").lower() == "true"
GENESIS_HOST = os.getenv("GENESIS_HOST", "http://127.0.0.1")
GENESIS_PORT = os.getenv("GENESIS_PORT", 5002)
SVN_SERVER_PARENT_URL = os.getenv("SVN_SERVER_PARENT_URL", "http://localhost/svn")
FILE_MAP = {
            'shading':'base',
            'concept':'none',
            'modeling':'base',
            'rigging':'base',
            'storyboard':'none',
            'layout':'layout',
            'previz':'layout',
            'animation':'anim',
            'lighting':'lighting',
            'fx':'fx',
            'rendering':'lighting',
            'compositing':'comp',
        }