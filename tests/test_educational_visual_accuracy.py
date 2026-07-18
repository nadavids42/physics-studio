import math

import pytest

from physics_playground.presentation.formatting import friendly_minutes, friendly_speed
from physics_playground.subjects.mechanics.inclined_plane.physics import (
    InclinedPlaneParameters,
    simulate,
)
from physics_playground.subjects.mechanics.inclined_plane.visuals import force_vectors


def _magnitude(vector: dict[str, object]) -> float:
    return math.hypot(float(vector["dx"]), float(vector["dy"]))


def test_inclined_plane_force_payload_uses_one_documented_linear_newton_scale():
    result = simulate(
        InclinedPlaneParameters(
            mass_kg=2,
            angle_deg=35,
            static_friction=0.4,
            kinetic_friction=0.25,
        )
    )
    vectors, scale = force_vectors(result)

    assert {vector["scale_mode"] for vector in vectors} == {"physical"}
    assert {vector["units"] for vector in vectors} == {"N"}
    assert {vector["pixels_per_unit"] for vector in vectors} == {scale}
    weight = next(vector for vector in vectors if vector["role"] == "gravity")
    normal = next(vector for vector in vectors if vector["role"] == "normal_force")
    assert _magnitude(weight) == pytest.approx(2 * result.parameters.gravity_m_s2)
    assert _magnitude(normal) == pytest.approx(result.normal_force_n)
    assert _magnitude(weight) * scale == pytest.approx(weight["display_length_px"])


def test_inclined_plane_visual_names_static_and_kinetic_friction_transition():
    static = simulate(InclinedPlaneParameters(angle_deg=5, static_friction=0.5))
    moving = simulate(
        InclinedPlaneParameters(angle_deg=45, static_friction=0.5, kinetic_friction=0.2)
    )
    static_vectors, _ = force_vectors(static)
    moving_vectors, _ = force_vectors(moving)

    assert "static friction" in next(
        str(vector["label"]) for vector in static_vectors if vector["role"] == "friction"
    )
    assert "kinetic friction" in next(
        str(vector["label"]) for vector in moving_vectors if vector["role"] == "friction"
    )
    assert next(vector for vector in moving_vectors if vector["role"] == "net_force")["dashed"]


def test_former_fun_comparisons_are_verified_unit_conversions():
    assert friendly_speed(10) == "10.00 m/s (36.0 km/h)"
    assert friendly_minutes(45) == "45.0 min"
    assert friendly_minutes(135) == "2 h 15 min"
