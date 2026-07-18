"""Discover metadata owned by simulation vertical slices."""

from importlib import import_module
from pkgutil import iter_modules
from types import ModuleType

SUBJECT_PACKAGES = (
    "physics_playground.subjects.mechanics",
    "physics_playground.subjects.waves_and_oscillations",
    "physics_playground.subjects.light_and_electricity",
    "physics_playground.subjects.fluids_and_matter",
)


def discover_metadata_modules() -> tuple[ModuleType, ...]:
    modules: list[ModuleType] = []
    for package_name in SUBJECT_PACKAGES:
        package = import_module(package_name)
        for child in sorted(iter_modules(package.__path__), key=lambda item: item.name):
            if not child.ispkg:
                continue
            module = import_module(f"{package_name}.{child.name}.metadata")
            if not hasattr(module, "SIMULATION") or not hasattr(module, "MISSIONS"):
                raise ValueError(f"Incomplete slice metadata: {module.__name__}")
            modules.append(module)
    return tuple(modules)


SLICE_METADATA_MODULES = discover_metadata_modules()
