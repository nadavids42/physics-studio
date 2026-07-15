from physics_playground.expansion_validation import validate_expansion_definition
from physics_playground.missions.definitions import MISSIONS_BY_SIMULATION
from physics_playground.subjects.waves_and_oscillations.manifests import WAVES_MANIFESTS
def test_waves_manifests_pass():
    for manifest in WAVES_MANIFESTS:validate_expansion_definition(manifest)
def test_wave_interference_has_four_missions():assert len(MISSIONS_BY_SIMULATION["wave_interference"])==4
def test_doppler_effect_has_four_missions():assert len(MISSIONS_BY_SIMULATION["doppler_effect"])==4
