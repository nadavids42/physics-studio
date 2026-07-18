"""Validated mission index discovered from simulation vertical slices."""

from physics_playground.missions.models import MissionDefinition, MissionType
from physics_playground.slice_catalog import SLICE_METADATA_MODULES

MISSION_DEFINITIONS = {
    mission.id: mission for module in SLICE_METADATA_MODULES for mission in module.MISSIONS
}
_mission_count = sum(len(module.MISSIONS) for module in SLICE_METADATA_MODULES)
if len(MISSION_DEFINITIONS) != _mission_count:
    raise ValueError("Mission IDs must be unique across simulation slices.")

MISSIONS_BY_SIMULATION = {
    module.SIMULATION.id: tuple(module.MISSIONS) for module in SLICE_METADATA_MODULES
}

__all__ = [
    "MISSION_DEFINITIONS",
    "MISSIONS_BY_SIMULATION",
    "MissionDefinition",
    "MissionType",
]
