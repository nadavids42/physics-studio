import pytest

from physics_playground.subjects.light_and_electricity.thin_lenses.physics import (
    LensType,
    ThinLensParameters,
    simulate,
)
from physics_playground.validation import PhysicsValidationError


def test_converging_lens_real_image():
    r = simulate(ThinLensParameters(3, 1))
    assert r.lens_type is LensType.CONVERGING
    assert r.image_distance_m == pytest.approx(1.5)
    assert r.magnification == pytest.approx(-0.5)
    assert r.real_image and r.inverted


def test_converging_inside_focus_is_virtual_upright():
    r = simulate(ThinLensParameters(0.5, 1))
    assert r.image_distance_m == pytest.approx(-1)
    assert r.magnification == pytest.approx(2)
    assert not r.real_image and not r.inverted


def test_diverging_lens_is_virtual():
    r = simulate(ThinLensParameters(3, -1))
    assert r.lens_type is LensType.DIVERGING
    assert r.image_distance_m == pytest.approx(-0.75)
    assert r.magnification == pytest.approx(0.25)
    assert not r.real_image


def test_exact_focal_point_is_explicit_infinity_case():
    r = simulate(ThinLensParameters(1, 1))
    assert r.singular and r.image_distance_m is None and r.magnification is None


def test_near_singular_case_is_flagged_and_finite():
    r = simulate(ThinLensParameters(1.00005, 1))
    assert r.near_singular and not r.singular
    assert r.image_distance_m > 10000


def test_lens_equation():
    r = simulate(ThinLensParameters(4, 1.5))
    assert 1 / r.parameters.focal_length_m == pytest.approx(
        1 / r.parameters.object_distance_m + 1 / r.image_distance_m
    )


@pytest.mark.parametrize(
    "p",
    [
        ThinLensParameters(0, 1),
        ThinLensParameters(1, 0),
        ThinLensParameters(1, 0.01),
        ThinLensParameters(1, 1, 0),
        ThinLensParameters(float("inf"), 1),
    ],
)
def test_invalid_parameters(p):
    with pytest.raises(PhysicsValidationError):
        simulate(p)
