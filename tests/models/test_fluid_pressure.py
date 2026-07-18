import pytest

from physics_playground.subjects.fluids_and_matter.fluid_pressure.physics import (
    FluidPressureParameters,
    simulate,
)
from physics_playground.validation import PhysicsValidationError


def test_gauge_pressure_is_rho_g_h():
    p = FluidPressureParameters(1000, 5, 9.81)
    r = simulate(p)
    assert r.gauge_pressure_pa == pytest.approx(49050)


def test_absolute_is_surface_plus_gauge():
    p = FluidPressureParameters(surface_pressure_pa=90000)
    r = simulate(p)
    assert r.absolute_pressure_pa == pytest.approx(90000 + r.gauge_pressure_pa)


def test_surface_gauge_pressure_is_zero():
    assert simulate(FluidPressureParameters(depth_m=0)).gauge_pressure_pa == 0


def test_pressure_doubles_with_depth_density_or_gravity():
    base = simulate(FluidPressureParameters(depth_m=2))
    deep = simulate(FluidPressureParameters(depth_m=4))
    dense = simulate(FluidPressureParameters(fluid_density_kg_m3=2000, depth_m=2))
    strong = simulate(FluidPressureParameters(depth_m=2, gravity_m_s2=19.62))
    assert deep.gauge_pressure_pa == pytest.approx(2 * base.gauge_pressure_pa)
    assert dense.gauge_pressure_pa == pytest.approx(2 * base.gauge_pressure_pa)
    assert strong.gauge_pressure_pa == pytest.approx(2 * base.gauge_pressure_pa)


def test_samples_cover_surface_and_bottom():
    r = simulate(FluidPressureParameters(maximum_depth_m=12, samples=7))
    assert r.samples[0].depth_m == 0
    assert r.samples[-1].depth_m == 12
    assert len(r.samples) == 7


@pytest.mark.parametrize(
    "p",
    [
        FluidPressureParameters(fluid_density_kg_m3=0),
        FluidPressureParameters(depth_m=-1),
        FluidPressureParameters(depth_m=11, maximum_depth_m=10),
        FluidPressureParameters(gravity_m_s2=0),
        FluidPressureParameters(surface_pressure_pa=-1),
        FluidPressureParameters(maximum_depth_m=0),
        FluidPressureParameters(samples=1),
        FluidPressureParameters(depth_m=float("inf")),
    ],
)
def test_invalid_parameters(p):
    with pytest.raises(PhysicsValidationError):
        simulate(p)
