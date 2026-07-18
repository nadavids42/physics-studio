import math

import numpy as np
import pytest

from physics_playground.subjects.waves_and_oscillations.double_pendulum.physics import (
    DoublePendulumParameters,
    simulate_double_pendulum,
)


def arrays(result):
    return [np.asarray(track.x) for track in result.animation.tracks] + [
        np.asarray(track.y) for track in result.animation.tracks
    ]


def test_identical_initial_states_remain_identical():
    r = simulate_double_pendulum(DoublePendulumParameters(perturbation_deg=0, duration_s=5))
    assert r.final_angular_separation_rad == pytest.approx(0, abs=1e-14)
    assert r.final_cartesian_separation_m == pytest.approx(0, abs=1e-14)


def test_correct_initial_perturbation():
    p = DoublePendulumParameters(perturbation_deg=0.25, duration_s=2)
    r = simulate_double_pendulum(p)
    assert r.initial_angular_separation_rad == pytest.approx(math.radians(0.25), rel=1e-12)


def test_energy_conservation_tolerance():
    r = simulate_double_pendulum(DoublePendulumParameters(duration_s=10, time_step_s=0.002))
    assert r.energy_drift_fraction < 1e-6


def test_better_convergence_at_smaller_time_step():
    fine = simulate_double_pendulum(DoublePendulumParameters(duration_s=10, time_step_s=0.002))
    coarse = simulate_double_pendulum(DoublePendulumParameters(duration_s=10, time_step_s=0.02))
    assert fine.energy_drift_fraction < coarse.energy_drift_fraction * 0.05


def test_repeatability_with_identical_settings():
    p = DoublePendulumParameters(duration_s=5, time_step_s=0.005)
    a = simulate_double_pendulum(p)
    b = simulate_double_pendulum(p)
    for left, right in zip(arrays(a), arrays(b), strict=True):
        assert np.array_equal(left, right)
