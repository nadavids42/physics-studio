from physics_playground.expansion_validation import validate_expansion_definition
from physics_playground.missions.definitions import MISSIONS_BY_SIMULATION
from physics_playground.subjects.light_and_electricity.manifests import OPTICS_MANIFESTS
def test_optics_manifests_pass():
    for manifest in OPTICS_MANIFESTS:validate_expansion_definition(manifest)
def test_each_optics_simulation_has_four_missions():
    assert len(MISSIONS_BY_SIMULATION["reflection_refraction"])==4;assert len(MISSIONS_BY_SIMULATION["thin_lenses"])==4
