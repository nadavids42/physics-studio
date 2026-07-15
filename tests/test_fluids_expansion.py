from physics_playground.expansion_validation import validate_expansion_definition
from physics_playground.missions.definitions import MISSIONS_BY_SIMULATION
from physics_playground.subjects.fluids_and_matter.manifests import FLUID_MANIFESTS
def test_fluid_manifests_pass():
    for manifest in FLUID_MANIFESTS:validate_expansion_definition(manifest)
def test_each_fluid_simulation_has_four_missions():
    assert len(MISSIONS_BY_SIMULATION["buoyancy"])==4
    assert len(MISSIONS_BY_SIMULATION["fluid_pressure"])==4
    assert len(MISSIONS_BY_SIMULATION["gas_laws"])==5
    assert len(MISSIONS_BY_SIMULATION["diffusion"])==5
