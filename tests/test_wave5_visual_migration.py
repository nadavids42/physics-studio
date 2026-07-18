from pathlib import Path

import pytest

from physics_playground.canvas.double_pendulum import SCENE as DOUBLE_SCENE
from physics_playground.canvas.double_pendulum import build_double_canvas
from physics_playground.canvas.earth_tunnel import (
    SCENE as TUNNEL_SCENE,
)
from physics_playground.canvas.earth_tunnel import (
    build_tunnel_canvas,
    build_tunnel_comparison_canvas,
)
from physics_playground.models.double_pendulum import (
    DoublePendulumParameters,
    simulate_double_pendulum,
)
from physics_playground.models.earth_tunnel import (
    TunnelModel,
    TunnelParameters,
    simulate_tunnel,
    uniform_acceleration,
)


def test_double_pendulum_uses_shared_assets_bounded_trails_and_accessible_identity():
    for token in (
        "PhysicsAssets.pivot",
        "PhysicsAssets.rod",
        "PhysicsAssets.pendulumBob",
        "PhysicsAnnotations.velocityTrail",
        "Baseline A (solid)",
        "Perturbed B (dashed)",
    ):
        assert token in DOUBLE_SCENE or token in build_double_canvas(
            simulate_double_pendulum(DoublePendulumParameters(duration_s=0.1)),
            seed=1,
            autoplay=False,
        )
    result = simulate_double_pendulum(DoublePendulumParameters(duration_s=0.1))
    payload = build_double_canvas(result, seed=1, autoplay=False)
    assert '"trailLength":72' in payload
    assert '"lineStyle":"solid"' in payload and '"lineStyle":"dashed"' in payload


def test_double_joint_and_bob_payloads_are_the_recorded_cartesian_tracks():
    result = simulate_double_pendulum(DoublePendulumParameters(duration_s=0.1, time_step_s=0.005))
    payload = build_double_canvas(result, seed=2, autoplay=False)
    for track in result.animation.tracks:
        assert f'"id":"{track.id}"' in payload
        assert f'"x":[{track.x[0]}' in payload
        assert f'"y":[{track.y[0]}' in payload


def test_double_separation_uses_track_coordinates_and_camera_is_fixed():
    result = simulate_double_pendulum(DoublePendulumParameters(duration_s=0.1))
    payload = build_double_canvas(
        result, seed=3, autoplay=False, show_separation=True, inspect_system="b"
    )
    assert "Math.hypot(a.x-b.x,(a.y||0)-(b.y||0))" in DOUBLE_SCENE
    assert '"camera":{"x":0,"y":0,"zoom":1}' in payload
    assert "Fixed camera" in DOUBLE_SCENE
    with pytest.raises(ValueError):
        build_double_canvas(result, seed=3, autoplay=False, inspect_system="unknown")


def test_tunnel_uses_shared_planet_mass_measurements_trail_and_normalized_acceleration():
    for token in (
        "PhysicsAssets.planet",
        "PhysicsAssets.mass",
        "PhysicsAnnotations.dimensionLine",
        "PhysicsAnnotations.centerOfMass",
        "PhysicsAnnotations.velocityTrail",
        "role:'acceleration'",
        "scale_mode:'normalized'",
        "Acceleration direction is physical",
    ):
        assert token in TUNNEL_SCENE


def test_tunnel_position_acceleration_and_turning_points_use_recorded_values():
    parameters = TunnelParameters(6_371_000, 9.81, 0.5)
    result = simulate_tunnel(parameters)
    payload = build_tunnel_canvas(result, seed=4, autoplay=False)
    position = result.animation.tracks[0].x
    acceleration = (
        next(plot for plot in result.plots if plot.id == "acceleration_position").series[0].y
    )
    assert f'"x":[{position[0]}' in payload
    assert f'"y":[{acceleration[0]}' in payload
    assert '"turningPointKm":3185.5' in payload
    assert max(position) == pytest.approx(parameters.radius_m * parameters.start_fraction / 1000)
    assert min(position) == pytest.approx(
        -parameters.radius_m * parameters.start_fraction / 1000, rel=2e-5
    )


def test_tunnel_acceleration_reverses_at_center_for_both_models():
    for model in TunnelModel:
        p = TunnelParameters(6_371_000, 9.81, model=model)
        result = simulate_tunnel(p)
        acceleration = (
            next(plot for plot in result.plots if plot.id == "acceleration_position").series[0].y
        )
        positions = result.animation.tracks[0].x
        assert acceleration[0] < 0
        first_negative = next(i for i, value in enumerate(positions) if value < 0)
        assert acceleration[first_negative] > 0
    uniform = TunnelParameters(6_371_000, 9.81)
    assert uniform_acceleration(1, uniform) < 0 and uniform_acceleration(-1, uniform) > 0


def test_tunnel_comparison_retains_one_synchronized_player_timeline_and_noncolor_identity():
    uniform = simulate_tunnel(TunnelParameters(6_371_000, 9.81, model=TunnelModel.UNIFORM))
    radial = simulate_tunnel(TunnelParameters(6_371_000, 9.81, model=TunnelModel.RADIAL))
    payload = build_tunnel_comparison_canvas(
        (("Uniform", uniform, ""), ("Radial", radial, "")), seed=5, autoplay=False
    )
    assert payload.count('"id":"traveler_') == 2
    assert '"frameCount":1000' in payload
    assert "dashed':'solid'" in TUNNEL_SCENE
    assert "Uniform-density planet vs. Radial-density profile" in payload


def test_wave5_chart_pages_use_shared_accessible_chart_renderer():
    root = Path(__file__).parents[1] / "physics_playground" / "pages"
    for name in ("double_pendulum.py", "earth_tunnel.py"):
        source = (root / name).read_text(encoding="utf-8")
        assert "render_chart" in source and "st.line_chart" not in source
