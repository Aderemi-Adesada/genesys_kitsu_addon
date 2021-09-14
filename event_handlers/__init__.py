from . import project_new, project_update

event_map = {
    # "asset:new": event_log,
    "project:new": project_new,
    "project:update": project_update,
}