"""Compatibility imports for the active mission UI adapter.

New code should import from :mod:`physics_playground.missions.ui`.
"""

from physics_playground.missions.ui import (
    GROUP_TO_SIMULATION,
    MISSION_GROUPS,
    MISSION_LABELS,
    SPEED_THINGS,
    complete,
    fun_speed,
    fun_time_minutes,
    init_missions,
    is_done,
    mission_checklist,
    prediction_quiz,
    process_run,
    sidebar_badges,
)

__all__ = [
    "GROUP_TO_SIMULATION",
    "MISSION_GROUPS",
    "MISSION_LABELS",
    "SPEED_THINGS",
    "complete",
    "fun_speed",
    "fun_time_minutes",
    "init_missions",
    "is_done",
    "mission_checklist",
    "prediction_quiz",
    "process_run",
    "sidebar_badges",
]
