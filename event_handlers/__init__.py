from . import (
    project_new,
    project_update,
    asset_update,
    shot_update,
    task_new,
    task_assign,
    task_unassign,
    )

event_map = {
    # "asset:new": event_log,
    "project:new": project_new,
    "project:update": project_update,
    "asset:update": asset_update,
    "shot:update": shot_update,
    "task:new": task_new,
    "task:assign": task_assign,
    "task:unassign":task_unassign
}