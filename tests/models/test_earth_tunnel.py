import math

import numpy as np
import pytest

from physics_playground.models.earth_tunnel import (
    TunnelModel,
    TunnelParameters,
    simulate_radial,
    simulate_uniform,
)
from physics_playground.validation import PhysicsValidationError


def test_symmetry_through_center():
    r = simulate_uniform(TunnelParameters(6371000, 9.81, samples=2001))
    x = np.asarray(r.animation.tracks[0].x)
    t = np.asarray(r.animation.time_s)
    half = r.period_s / 2
    for index in np.linspace(0, 900, 12, dtype=int):
        opposite = np.interp(t[index] + half, t, x)
        assert opposite == pytest.approx(-x[index], rel=2e-5)


def test_maximum_speed_occurs_at_center():
    r = simulate_uniform(TunnelParameters(6371000, 9.81, samples=2001))
    x = np.abs(np.asarray(r.animation.tracks[0].x))
    speed = np.abs(np.asarray(r.plots[1].series[0].y))
    assert x[np.argmax(speed)] < 10


def test_uniform_density_period():
    p = TunnelParameters(6371000, 9.81)
    assert simulate_uniform(p).period_s == pytest.approx(
        2 * math.pi * math.sqrt(p.radius_m / p.surface_gravity_m_s2)
    )


def test_energy_conservation_uniform_and_radial():
    assert simulate_uniform(TunnelParameters(6371000, 9.81)).energy_drift_fraction < 1e-12
    assert (
        simulate_radial(
            TunnelParameters(6371000, 9.81, model=TunnelModel.RADIAL, samples=4000)
        ).energy_drift_fraction
        < 1e-5
    )


def test_period_scales_with_inverse_square_root_density():
    low = simulate_uniform(TunnelParameters(3_000_000, 5))
    high = simulate_uniform(TunnelParameters(3_000_000, 20))
    assert low.period_s / high.period_s == pytest.approx(math.sqrt(20 / 5))


@pytest.mark.parametrize(
    "parameters",
    [
        TunnelParameters(-1, 9.81),
        TunnelParameters(1000, 0),
        TunnelParameters(1000, 9.81, 0),
        TunnelParameters(1000, 9.81, 1.2),
        TunnelParameters(1000, 9.81, model=TunnelModel.RADIAL, density_gradient=1.0),
    ],
)
def test_custom_planet_validation(parameters):
    with pytest.raises(PhysicsValidationError):
        simulate_uniform(
            parameters
        ) if parameters.model == TunnelModel.UNIFORM else simulate_radial(parameters)
