import pytest

from physics_playground.subjects.mechanics.roller_coaster.physics import (
    RollerCoasterParameters,
    simulate,
)
from physics_playground.validation import PhysicsValidationError


def test_lossless_mechanical_energy_is_conserved():
    r = simulate(RollerCoasterParameters())
    assert max(r.mechanical_energy_j) - min(r.mechanical_energy_j) == pytest.approx(0, abs=1e-8)


def test_speed_matches_energy_formula_at_finish():
    p = RollerCoasterParameters(initial_height_m=20, hill_height_m=10, final_height_m=5)
    r = simulate(p)
    expected = (2 * p.gravity_m_s2 * (20 - 5)) ** 0.5
    assert r.speed_m_s[-1] == pytest.approx(expected)


def test_impossibly_high_hill_stops_track():
    r = simulate(RollerCoasterParameters(initial_height_m=10, hill_height_m=30))
    assert not r.completed and r.stopping_distance_m is not None


def test_losses_reduce_mechanical_energy_linearly():
    p = RollerCoasterParameters(loss_per_meter_j=100)
    r = simulate(p)
    assert r.mechanical_energy_j[-1] == pytest.approx(
        r.mechanical_energy_j[0] - 100 * r.distance_m[-1]
    )


def test_mass_cancels_from_lossless_speed():
    a = simulate(RollerCoasterParameters(mass_kg=100))
    b = simulate(RollerCoasterParameters(mass_kg=500))
    assert a.speed_m_s == pytest.approx(b.speed_m_s)


@pytest.mark.parametrize(
    "p",
    [
        RollerCoasterParameters(mass_kg=0),
        RollerCoasterParameters(initial_height_m=-1),
        RollerCoasterParameters(loss_per_meter_j=-1),
        RollerCoasterParameters(track_length_m=0),
        RollerCoasterParameters(samples=2),
        RollerCoasterParameters(gravity_m_s2=float("nan")),
    ],
)
def test_invalid_parameters(p):
    with pytest.raises(PhysicsValidationError):
        simulate(p)
