import math

import numpy as np
import pytest

from physics_playground.subjects.waves_and_oscillations.boing.physics import (
    SpringParameters,
    simulate_damped_driven,
    simulate_undamped,
)


def test_analytical_period():
    p = SpringParameters(2, 20, 1, duration_s=10, samples=1000)
    r = simulate_undamped(p)
    assert r.period_s == pytest.approx(2 * math.pi * math.sqrt(2 / 20))


def test_ideal_period_is_amplitude_independent():
    a = simulate_undamped(SpringParameters(2, 20, 0.2))
    b = simulate_undamped(SpringParameters(2, 20, 2))
    assert a.period_s == b.period_s


def test_energy_is_conserved_without_damping():
    r = simulate_undamped(SpringParameters(2, 20, 1, duration_s=20, samples=1000))
    energy = np.asarray(r.plots[2].series[0].y)
    assert np.ptp(energy) < 1e-10


def test_energy_decays_with_damping():
    r = simulate_damped_driven(
        SpringParameters(2, 20, 1, damping_n_s_m=1, duration_s=20, samples=1500)
    )
    energy = np.asarray(r.plots[2].series[0].y)
    assert energy[-1] < energy[0] * 0.01


def test_resonant_drive_produces_larger_late_response():
    off = simulate_damped_driven(SpringParameters(2, 20, 0.01, 0.3, 4, 0.5, 40, 2000))
    near = simulate_damped_driven(SpringParameters(2, 20, 0.01, 0.3, 4, 1, 40, 2000))
    assert near.late_response_amplitude_m > off.late_response_amplitude_m * 2
