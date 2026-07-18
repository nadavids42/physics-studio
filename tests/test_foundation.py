"""Structural checkpoint tests; these do not alter legacy simulation behavior."""

import numpy as np

from physics_playground.integrators import rk4_step
from physics_playground.missions import MISSION_DEFINITIONS
from physics_playground.registry import SIMULATION_REGISTRY
from physics_playground.validation import validate_trajectory


def test_registry_contains_all_twenty_two_simulations() -> None:
    assert len(SIMULATION_REGISTRY) == 22
    assert len({item.id for item in SIMULATION_REGISTRY}) == 22


def test_every_registry_group_has_missions() -> None:
    groups = {mission.group for mission in MISSION_DEFINITIONS.values()}
    assert all(item.mission_group in groups for item in SIMULATION_REGISTRY)


def test_trajectory_contract_accepts_matching_finite_arrays() -> None:
    time = np.array([0.0, 0.5, 1.0])
    position = np.array([0.0, 1.0, 0.0])
    validate_trajectory(time, {"position": position})


def test_rk4_integrates_constant_derivative() -> None:
    state = np.array([0.0])
    result = rk4_step(lambda current, time: np.array([2.0]), state, 0.0, 0.5)
    assert np.allclose(result, [1.0])
