"""Validated simulation index discovered from vertical-slice metadata."""

from importlib import import_module
from types import ModuleType

from physics_playground.models.simulations import InteractiveMode
from physics_playground.slice_catalog import SLICE_METADATA_MODULES

LEARNING_MODES = tuple(InteractiveMode)
SIMULATION_REGISTRY = tuple(module.SIMULATION for module in SLICE_METADATA_MODULES)
SIMULATIONS_BY_ID = {definition.id: definition for definition in SIMULATION_REGISTRY}

if len(SIMULATIONS_BY_ID) != len(SIMULATION_REGISTRY):
    raise ValueError("Simulation IDs must be unique across vertical slices.")
for definition in SIMULATION_REGISTRY:
    if definition.page_module.rsplit(".", 1)[0] != (
        f"physics_playground.subjects."
        f"{next(module.__name__.split('.')[2] for module in SLICE_METADATA_MODULES if module.SIMULATION is definition)}."
        f"{definition.id}"
    ):
        raise ValueError(f"Simulation {definition.id!r} metadata is not colocated with its page.")


def load_validated_page(simulation_id: str) -> tuple[ModuleType, str]:
    """Resolve a simulation page only after validating its manifest."""

    catalog = import_module("physics_playground.expansion_catalog")
    validation = import_module("physics_playground.expansion_validation")
    manifest = catalog.EXPANSION_BY_ID[simulation_id]
    validation.validate_expansion_definition(manifest)
    module_name, function_name = manifest.page_entrypoint.rsplit(".", 1)
    return import_module(module_name), function_name
