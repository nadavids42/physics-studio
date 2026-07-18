from physics_playground.expansion_validation import validate_expansion_definition
from physics_playground.missions.definitions import MISSIONS_BY_SIMULATION
from physics_playground.subjects.light_and_electricity.manifests import MAGNETIC_FORCE_MANIFEST


def test_magnetic_force_manifest_passes():
    validate_expansion_definition(MAGNETIC_FORCE_MANIFEST)


def test_magnetic_force_has_five_missions():
    assert len(MISSIONS_BY_SIMULATION["magnetic_forces"]) == 5
