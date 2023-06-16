from . import (
    project_new,
    project_update,
    asset_new,
    asset_update,
    episode_new,
    episode_update,
    sequence_new,
    sequence_update,
    shot_new,
    shot_update,
    edit_new,
    edit_update,
    task_new,
    task_assign,
    task_unassign,
    task_status,
    comment_new,
    shot_casting_update,
    asset_casting_update,
    entity_link_new,
    entity_link_update,
    )

event_map = {
    "project:new": project_new,
    "project:update": project_update,
    "asset:new": asset_new,
    "asset:update": asset_update,
    "episode:new": episode_new,
    "episode:update": episode_update,
    "sequence:new": sequence_new,
    "sequence:update": sequence_update,
    "shot:new": shot_new,
    "shot:update": shot_update,
    "edit:new": edit_new,
    "edit:update": edit_update,
    "task:new": task_new,
    "task:assign": task_assign,
    "task:unassign":task_unassign,
    "task:status-changed":task_status,
    "comment:new":comment_new,
    "shot:casting-update":shot_casting_update,
    "asset:casting-update": asset_casting_update,
    "entity-link:new": entity_link_new,
    "entity-link:update": entity_link_update,
}