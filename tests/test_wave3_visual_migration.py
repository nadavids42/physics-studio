import math
from pathlib import Path

import pytest

from physics_playground.subjects.mechanics.canvas import SCENE, document
from physics_playground.subjects.mechanics.center_of_mass.physics import (
    CenterOfMassParameters,
)
from physics_playground.subjects.mechanics.center_of_mass.physics import (
    simulate as simulate_center,
)
from physics_playground.subjects.mechanics.inclined_plane.physics import (
    InclinedPlaneParameters,
)
from physics_playground.subjects.mechanics.inclined_plane.physics import (
    simulate as simulate_incline,
)
from physics_playground.subjects.mechanics.rotational_motion.physics import (
    RotationalParameters,
)
from physics_playground.subjects.mechanics.rotational_motion.physics import (
    simulate as simulate_rotation,
)
from physics_playground.subjects.mechanics.torque_levers.physics import (
    LeverParameters,
)
from physics_playground.subjects.mechanics.torque_levers.physics import (
    simulate as simulate_lever,
)


def test_incline_scene_uses_shared_geometry_and_declares_vector_semantics():
    for token in (
        "PhysicsAssets.ramp",
        "PhysicsAssets.block",
        "PhysicsAnnotations.normalLine",
        "PhysicsAnnotations.angleArc",
        "PhysicsAnnotations.pathGuide",
        "PhysicsAnnotations.vectorSet",
        "scale_mode",
    ):
        assert token in SCENE
    result = simulate_incline(
        InclinedPlaneParameters(angle_deg=30, static_friction=0.9, kinetic_friction=0.4)
    )
    assert result.acceleration_m_s2 == 0
    payload = document(
        "ramp",
        [{"id": "block", "x": [0, 0]}],
        message=result.outcome,
        seed=3,
        scene_config={"angleDeg": 30, "criticalAngleDeg": result.critical_angle_deg},
    )
    assert '"angleDeg":30' in payload
    assert '"criticalAngleDeg"' in payload


def test_incline_force_components_and_friction_direction_remain_physical():
    result = simulate_incline(
        InclinedPlaneParameters(mass_kg=2, angle_deg=40, static_friction=0.2, kinetic_friction=0.1)
    )
    theta = math.radians(40)
    assert result.normal_force_n == pytest.approx(2 * 9.81 * math.cos(theta))
    assert result.down_slope_force_n == pytest.approx(2 * 9.81 * math.sin(theta))
    assert result.friction_force_n > 0 and result.net_force_n > 0


def test_lever_scene_has_distinct_force_dimension_and_torque_annotations():
    for token in (
        "PhysicsAssets.rod",
        "PhysicsAssets.pivot",
        "PhysicsAssets.block",
        "PhysicsAnnotations.dimensionLine",
        "PhysicsAnnotations.centerOfMass",
        "PhysicsAnnotations.vectorSet",
        "PhysicsAssets.torqueArc",
    ):
        assert token in SCENE
    balanced = simulate_lever(
        LeverParameters(load_force_n=100, load_arm_m=1, effort_force_n=50, effort_arm_m=2)
    )
    assert balanced.net_torque_n_m == pytest.approx(0)
    assert "Math.abs(c.netTorqueNm||0)>1e-9" in SCENE


def test_center_marker_and_bounded_illustrative_radius_contract():
    equal = simulate_center(CenterOfMassParameters(2, -3, 2, 3))
    unequal = simulate_center(CenterOfMassParameters(2, -2, 6, 2))
    assert equal.center_of_mass_m == pytest.approx(0)
    assert unequal.center_of_mass_m == pytest.approx(1)
    for token in (
        "PhysicsAssets.mass",
        "PhysicsAssets.ruler",
        "PhysicsAnnotations.centerOfMass",
        "Math.max(11,Math.min(24",
        "Mass radii are bounded illustrations",
    ):
        assert token in SCENE


def test_rotation_orientation_uses_recorded_angle_but_is_visually_bounded():
    result = simulate_rotation(RotationalParameters(torque_n_m=10, duration_s=10))
    assert result.angular_position_rad[-1] > 2 * math.pi
    payload = document(
        "rotation",
        [{"id": "body", "x": [0, result.angular_position_rad[-1]]}],
        message=result.outcome,
        seed=4,
        scene_config={"torqueNm": 10},
    )
    assert f"{result.angular_position_rad[-1]}" in payload
    assert "total%(Math.PI*2)" in SCENE
    assert "Angular indicators are schematic" in SCENE


def test_wave3_pages_use_shared_charts_and_separate_rotation_units():
    root = Path(__file__).parents[1] / "physics_playground" / "subjects" / "mechanics"
    sources = [
        (root / simulation / "page.py").read_text(encoding="utf-8")
        for simulation in ("center_of_mass", "inclined_plane", "rotational_motion", "torque_levers")
    ]
    assert all("render_chart" in source and "st.line_chart" not in source for source in sources)
    assert sources[2].count("series_figure(") == 3
