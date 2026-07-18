import pytest

from physics_playground.subjects.fluids_and_matter.buoyancy.physics import (
    BuoyancyInputMode,
    BuoyancyParameters,
    BuoyancyState,
    simulate,
)
from physics_playground.validation import PhysicsValidationError


def test_less_dense_object_floats_with_density_ratio_submerged():
    r = simulate(BuoyancyParameters(object_density_kg_m3=600, fluid_density_kg_m3=1000))
    assert r.state is BuoyancyState.FLOATING
    assert r.submerged_fraction == pytest.approx(0.6)
    assert r.buoyant_force_n == pytest.approx(r.weight_n)
    assert r.apparent_weight_n == 0


def test_denser_object_sinks_and_has_positive_apparent_weight():
    r = simulate(BuoyancyParameters(object_density_kg_m3=1200, fluid_density_kg_m3=1000))
    assert r.state is BuoyancyState.SINKING
    assert r.submerged_fraction == 1
    assert r.apparent_weight_n == pytest.approx(r.weight_n - r.maximum_buoyant_force_n)
    assert r.net_vertical_force_n < 0


def test_equal_density_is_neutral():
    r = simulate(BuoyancyParameters(object_density_kg_m3=1000, fluid_density_kg_m3=1000))
    assert r.state is BuoyancyState.NEUTRAL
    assert r.buoyant_force_n == pytest.approx(r.weight_n)
    assert r.net_vertical_force_n == pytest.approx(0)


def test_mass_input_calculates_effective_density():
    r = simulate(BuoyancyParameters(BuoyancyInputMode.MASS, 999, 8, 0.01, 1000))
    assert r.effective_density_kg_m3 == pytest.approx(800)
    assert r.effective_mass_kg == 8
    assert r.submerged_fraction == pytest.approx(0.8)


def test_floating_fraction_is_independent_of_gravity():
    earth = simulate(BuoyancyParameters(gravity_m_s2=9.81))
    moon = simulate(BuoyancyParameters(gravity_m_s2=1.62))
    assert earth.submerged_fraction == moon.submerged_fraction


@pytest.mark.parametrize(
    "p",
    [
        BuoyancyParameters(object_density_kg_m3=0),
        BuoyancyParameters(object_mass_kg=0),
        BuoyancyParameters(object_volume_m3=0),
        BuoyancyParameters(fluid_density_kg_m3=-1),
        BuoyancyParameters(gravity_m_s2=float("nan")),
    ],
)
def test_invalid_parameters(p):
    with pytest.raises(PhysicsValidationError):
        simulate(p)
