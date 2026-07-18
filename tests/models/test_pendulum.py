import math

import pytest

from physics_playground.models.pendulum import (
    PendulumModel,
    PendulumParameters,
    simulate_nonlinear,
    simulate_small_angle,
)


def test_small_angle_period():
    r = simulate_small_angle(PendulumParameters(2, 9.81, 5))
    assert r.period_s == pytest.approx(2 * math.pi * math.sqrt(2 / 9.81))


def test_period_gravity_dependence():
    earth = simulate_small_angle(PendulumParameters(2, 9.81, 5))
    moon = simulate_small_angle(PendulumParameters(2, 1.62, 5))
    assert moon.period_s / earth.period_s == pytest.approx(math.sqrt(9.81 / 1.62))


def test_period_length_dependence():
    short = simulate_small_angle(PendulumParameters(1, 9.81, 5))
    long = simulate_small_angle(PendulumParameters(4, 9.81, 5))
    assert long.period_s / short.period_s == pytest.approx(2)


def test_nonlinear_energy_conservation():
    r = simulate_nonlinear(PendulumParameters(2, 9.81, 70, PendulumModel.NONLINEAR, samples=3000))
    assert r.energy_drift_fraction < 1e-6


def test_models_agree_at_small_angles():
    a = simulate_small_angle(PendulumParameters(2, 9.81, 3))
    b = simulate_nonlinear(PendulumParameters(2, 9.81, 3, PendulumModel.NONLINEAR))
    assert abs(a.period_s - b.period_s) / a.period_s < 0.001


def test_disagreement_grows_at_large_angles():
    small_a = simulate_small_angle(PendulumParameters(2, 9.81, 5))
    small_b = simulate_nonlinear(PendulumParameters(2, 9.81, 5, PendulumModel.NONLINEAR))
    large_a = simulate_small_angle(PendulumParameters(2, 9.81, 80))
    large_b = simulate_nonlinear(PendulumParameters(2, 9.81, 80, PendulumModel.NONLINEAR))
    assert abs(large_b.period_s - large_a.period_s) > 20 * abs(small_b.period_s - small_a.period_s)
