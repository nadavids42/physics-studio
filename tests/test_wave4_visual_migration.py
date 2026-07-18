from pathlib import Path

import pytest

from physics_playground.canvas.boing import SCENE as BOING_SCENE
from physics_playground.canvas.boing import build_boing_canvas
from physics_playground.models.spring import SpringParameters, simulate_spring
from physics_playground.subjects.mechanics.canvas import SCENE as MECHANICS_SCENE
from physics_playground.subjects.mechanics.canvas import document
from physics_playground.subjects.mechanics.roller_coaster.physics import (
    RollerCoasterParameters,
    simulate,
)
from physics_playground.visual.assets import AssetKind


def test_track_is_a_shared_scientific_asset_and_coaster_uses_it():
    assert AssetKind.TRACK.value == "track"
    for token in (
        "PhysicsAssets.track",
        "PhysicsAssets.cart",
        "PhysicsAssets.ruler",
        "PhysicsAnnotations.motionDirection",
        "Unreachable with",
    ):
        assert token in MECHANICS_SCENE
    assert "Math.sin(car.x" not in MECHANICS_SCENE


def test_coaster_document_uses_model_track_distance_height_and_speed_samples():
    result = simulate(
        RollerCoasterParameters(
            initial_height_m=24, hill_height_m=14, final_height_m=3, track_length_m=80
        )
    )
    normalized = [distance / result.parameters.track_length_m for distance in result.distance_m]
    payload = document(
        "coaster",
        [{"id": "car", "x": normalized, "y": list(result.speed_m_s)}],
        message=result.outcome,
        seed=9,
        scene_config={
            "trackLengthM": 80,
            "trackPoints": [
                {"distance": 0, "height": 24},
                {"distance": 40, "height": 14},
                {"distance": 80, "height": 3},
            ],
            "reachableDistanceM": result.distance_m[-1],
        },
    )
    assert '"height":24' in payload and '"height":14' in payload and '"height":3' in payload
    assert f'"reachableDistanceM":{result.distance_m[-1]}' in payload
    assert f'"y":[{result.speed_m_s[0]}' in payload


def test_unreachable_coaster_samples_stop_before_the_unreachable_point():
    result = simulate(
        RollerCoasterParameters(
            initial_height_m=5, hill_height_m=30, final_height_m=0, initial_speed_m_s=0
        )
    )
    assert not result.completed and result.stopping_distance_m is not None
    assert result.distance_m[-1] < result.stopping_distance_m
    assert all(distance < result.stopping_distance_m for distance in result.distance_m)


def test_lossy_coaster_mechanical_energy_decreases_by_modeled_loss():
    result = simulate(RollerCoasterParameters(loss_per_meter_j=100))
    for distance, energy in zip(result.distance_m, result.mechanical_energy_j, strict=True):
        assert result.mechanical_energy_j[0] - energy == pytest.approx(100 * distance)
    assert "Mechanical energy decreases by the modeled loss per meter" in MECHANICS_SCENE


def test_boing_uses_recorded_position_and_velocity_without_phase_changes():
    result = simulate_spring(SpringParameters(2, 20, 1, 0.4, 3, 1, 10, 180))
    payload = build_boing_canvas(result, seed=5, autoplay=False)
    position = result.animation.tracks[0].x
    velocity = next(plot for plot in result.plots if plot.id == "velocity_time").series[0].y
    assert f'"x":[{position[0]}' in payload
    assert f'"y":[{velocity[0]}' in payload
    assert "Math.sin" not in BOING_SCENE and "Math.cos" not in BOING_SCENE


def test_boing_shared_assets_references_and_vector_semantics():
    for token in (
        "PhysicsAssets.spring",
        "PhysicsAssets.mass",
        "PhysicsAnnotations.pathGuide",
        "PhysicsAnnotations.velocityTrail",
        "PhysicsAnnotations.vectorSet",
        "PhysicsAnnotations.dimensionLine",
        "damping envelope",
        "scale_mode:'physical'",
        "scale_mode:'normalized'",
        "restoring=-",
    ):
        assert token in BOING_SCENE
    assert "equilibrium=t.x(0)" in BOING_SCENE


def test_wave4_analysis_pages_use_accessible_shared_chart_rendering():
    root = Path(__file__).parents[1] / "physics_playground"
    coaster = (root / "subjects/mechanics/roller_coaster/page.py").read_text(encoding="utf-8")
    boing = (root / "pages/boing.py").read_text(encoding="utf-8")
    assert (
        "series_figure(" in coaster and "render_chart" in coaster and "st.line_chart" not in coaster
    )
    assert "render_chart" in boing and "st.line_chart" not in boing
