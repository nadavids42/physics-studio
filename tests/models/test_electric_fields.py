import pytest

from physics_playground.subjects.light_and_electricity.electric_fields.physics import (
    COULOMB_CONSTANT,
    MAX_FIELD_POINTS,
    ElectricFieldParameters,
    PointCharge,
    field_at,
    simulate,
)
from physics_playground.validation import PhysicsValidationError


def test_single_positive_charge_field_and_potential():
    ex, ey, v = field_at((PointCharge(1e-6, 0, 0),), 1, 0, 0.01)
    assert ex == pytest.approx(COULOMB_CONSTANT * 1e-6)
    assert ey == pytest.approx(0)
    assert v == pytest.approx(COULOMB_CONSTANT * 1e-6)


def test_negative_charge_field_points_toward_charge():
    assert field_at((PointCharge(-1e-6, 0, 0),), 1, 0, 0.01)[0] < 0


def test_superposition_cancels_between_equal_like_charges():
    ex, ey, v = field_at((PointCharge(1e-6, -1, 0), PointCharge(1e-6, 1, 0)), 0, 0, 0.1)
    assert ex == pytest.approx(0, abs=1e-12)
    assert ey == pytest.approx(0, abs=1e-12)
    assert v > 0


def test_force_on_test_charge_is_q_times_field():
    r = simulate(
        ElectricFieldParameters(
            (PointCharge(1e-6, 0, 0),), test_charge_c=-2e-6, test_x_m=1, test_y_m=0
        )
    )
    assert r.force_x_n == pytest.approx(-2e-6 * r.test_field_x_n_c)
    assert r.force_y_n == pytest.approx(-2e-6 * r.test_field_y_n_c)


def test_zero_test_charge_has_zero_force_but_field_remains():
    r = simulate(ElectricFieldParameters(test_charge_c=0))
    assert r.force_magnitude_n == 0 and r.test_field_magnitude_n_c > 0


def test_grid_excludes_source_singularities():
    r = simulate(
        ElectricFieldParameters((PointCharge(1e-6, 0, 0),), test_x_m=1, test_y_m=0, grid_size=25)
    )
    assert r.excluded_points >= 1
    assert any(s.potential_v is None for s in r.samples)


def test_deterministic_result():
    p = ElectricFieldParameters()
    assert simulate(p) == simulate(p)


def test_maximum_grid_budget_is_explicit():
    assert 49**2 <= MAX_FIELD_POINTS and 50**2 > MAX_FIELD_POINTS


@pytest.mark.parametrize(
    "p",
    [
        ElectricFieldParameters(()),
        ElectricFieldParameters((PointCharge(0, 0, 0),)),
        ElectricFieldParameters(test_x_m=-1, test_y_m=0),
        ElectricFieldParameters(extent_m=0),
        ElectricFieldParameters(minimum_distance_m=0),
        ElectricFieldParameters(grid_size=8),
        ElectricFieldParameters(grid_size=50),
        ElectricFieldParameters(test_charge_c=float("nan")),
    ],
)
def test_invalid_singular_and_boundary_parameters(p):
    with pytest.raises(PhysicsValidationError):
        simulate(p)


def test_direct_singularity_evaluation_is_rejected():
    with pytest.raises(PhysicsValidationError):
        field_at((PointCharge(1e-6, 0, 0),), 0, 0, 0.1)
