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

LOGIN_NAME = os.getenv("LOGIN_NAME", "email")
USE_ROCKET_CHAT_BOT = os.getenv("USE_ROCKET_CHAT_BOT", "False").lower() == "true"
RC_USER = os.getenv("RC_USER", None)
RC_USER_PASSWORD = os.getenv("RC_USER_PASSWORD", None)
# RC_USER_TOKEN = os.getenv("RC_USER_TOKEN", None)
RC_SERVER_URL = os.getenv("RC_SERVER_URL", None)
