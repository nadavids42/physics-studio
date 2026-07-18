"""Shared architecture models; simulation contracts live in vertical slices."""

from physics_playground.models.simulations import (
    Difficulty,
    LearningMode,
    SimulationDefinition,
    VisualMetadata,
)

__all__ = [
    "Difficulty",
    "LearningMode",
    "SimulationDefinition",
    "VisualMetadata",
]


def __getattr__(name: str) -> object:
    """Forward deprecated mode imports through the warning-producing compatibility shim."""

    if name in {"InteractiveMode", "SimulationMode"}:
        from physics_playground.models import simulations

        return getattr(simulations, name)
    raise AttributeError(name)
