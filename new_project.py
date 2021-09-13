from .config import GENESIS_HOST, GENESIS_PORT, SVN_SERVER_PARENT_URL
import requests
import gazu


def handle_event(data):
    project_name = data['name']
    requests.post(url=f"{GENESIS_HOST}:{GENESIS_PORT}/project/{project_name}")
    svn_url = os.path.join(SVN_SERVER_PARENT_URL, project_name.replace(' ', '_').lower())
    if data['production_type'] == 'tvshow':
        data.update({'file_tree': file_tree_service.get_tree_from_file('eaxum_tv_show'), 'data': {'local_svn_url': svn_url, 'remote_svn_url': svn_url}})
    else:
        data.update({'file_tree': file_tree_service.get_tree_from_file('eaxum'), 'data': {'file_map': FILE_MAP, 'svn_url': svn_url}})
    print(data)