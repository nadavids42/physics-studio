"""Compatibility imports for the renamed binding model module.

New code should import from :mod:`physics_playground.binding_models`.
"""

from physics_playground.binding_models import (
    ExpectedMetric,
    MetricDefinition,
    SimulationBinding,
    SimulationPreset,
)

__all__ = [
    "ExpectedMetric",
    "MetricDefinition",
    "SimulationBinding",
    "SimulationPreset",
]
