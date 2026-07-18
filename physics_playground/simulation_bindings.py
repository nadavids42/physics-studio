"""Compatibility imports for the renamed binding catalog.

New code should import from :mod:`physics_playground.binding_catalog`.
"""

from physics_playground.binding_catalog import (
    PROJECTILE_BINDING,
    PROJECTILE_WORKED_EXAMPLE_PRESET,
    SIMULATION_BINDINGS,
    SIMULATION_PRESETS,
    binding_for,
    preset_for,
)

__all__ = [
    "PROJECTILE_BINDING",
    "PROJECTILE_WORKED_EXAMPLE_PRESET",
    "SIMULATION_BINDINGS",
    "SIMULATION_PRESETS",
    "binding_for",
    "preset_for",
]
