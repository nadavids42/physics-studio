from physics_playground.expansion_validation import validate_expansion_definition
from physics_playground.missions.definitions import MISSIONS_BY_SIMULATION
from physics_playground.registry import SIMULATIONS_BY_ID
from physics_playground.subjects.mechanics.manifests import MECHANICS_MANIFESTS


def test_all_mechanics_manifests_pass_enrollment_gate():
    for item in MECHANICS_MANIFESTS:
        validate_expansion_definition(item)


def test_each_mechanics_simulation_has_three_missions_and_four_modes():
    for simulation_id in (
        "inclined_plane",
        "torque_levers",
        "center_of_mass",
        "roller_coaster",
        "rotational_motion",
    ):
        assert len(MISSIONS_BY_SIMULATION[simulation_id]) >= 3
        assert len(SIMULATIONS_BY_ID[simulation_id].modes) == 4
