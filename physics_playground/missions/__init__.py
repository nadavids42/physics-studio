"""Mission domain models with lazy catalog access."""

from typing import Any

from physics_playground.missions.models import MissionDefinition, MissionType


def __getattr__(name: str) -> Any:
    if name in {"MISSION_DEFINITIONS", "MISSIONS_BY_SIMULATION"}:
        from physics_playground.missions import definitions

        return getattr(definitions, name)
    raise AttributeError(name)


__all__ = ["MISSION_DEFINITIONS", "MISSIONS_BY_SIMULATION", "MissionDefinition", "MissionType"]
