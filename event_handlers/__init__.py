from . import (
    project_new,
    project_update,
    asset_new,
    asset_update,
    shot_new,
    shot_update,
    task_new,
    task_assign,
    task_unassign,
    task_status,
    comment_new,
    )

event_map = {
    "project:new": project_new,
    "project:update": project_update,
    "asset:new": asset_new,
    "asset:update": asset_update,
    "shot:new": shot_new,
    "shot:update": shot_update,
    "task:new": task_new,
    "task:assign": task_assign,
    "task:unassign":task_unassign,
    "task:status-changed":task_status,
    "comment:new":comment_new,
}