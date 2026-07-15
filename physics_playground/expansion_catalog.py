"""Single catalog for every simulation delivered in expansion Prompts 20B–20L."""
from importlib import import_module
from physics_playground.subjects.mechanics.manifests import MECHANICS_MANIFESTS
from physics_playground.subjects.waves_and_oscillations.manifests import WAVES_MANIFESTS
from physics_playground.subjects.light_and_electricity.manifests import LIGHT_ELECTRICITY_MANIFESTS
from physics_playground.subjects.fluids_and_matter.manifests import FLUID_MANIFESTS

EXPANSION_MANIFESTS=(*MECHANICS_MANIFESTS,*WAVES_MANIFESTS,*LIGHT_ELECTRICITY_MANIFESTS,*FLUID_MANIFESTS)
EXPANSION_BY_ID={item.metadata.id:item for item in EXPANSION_MANIFESTS}

def resolve_entrypoint(path:str):
    module,name=path.rsplit(".",1);return getattr(import_module(module),name)

def parameter_type(manifest):
    module=import_module(manifest.physics_entrypoint.rsplit(".",1)[0]);return getattr(module,manifest.parameter_model)
