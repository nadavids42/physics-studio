"""Contract tests for the browser-side player document."""

from physics_playground.canvas.bumper_cars import (
    build_bumper_canvas,
    build_bumper_comparison_canvas,
)
from physics_playground.canvas.player import build_player_document
from physics_playground.models.collision import CollisionParameters, simulate_collision


def test_shared_player_contains_required_controls_and_accessibility() -> None:
    document = build_player_document(
        config={
            "durationMs": 1000,
            "autoplay": False,
            "seed": 7,
            "tracks": [],
            "events": [],
        },
        scene_javascript="const scene={draw(){}};",
        logical_width=640,
        logical_height=320,
        accessible_label="Test animation",
        idle_hint="Press play",
    )
    assert 'id="play-pause"' in document
    assert 'id="replay"' in document
    assert 'id="scrubber"' in document
    assert 'id="speed"' in document
    assert 'aria-live="polite"' in document
    assert "ResizeObserver" in document
    assert "devicePixelRatio" in document
    assert "prefers-reduced-motion" in document
    assert "seededRandom" in document
    assert "keydown" in document
    assert "high-contrast" in document
    assert "reducedMotion" in document


def test_bumper_canvas_uses_tracks_and_structured_impact_event() -> None:
    result = simulate_collision(CollisionParameters(2.0, 2.0, 4.0, 0.0, 1.0))
    document = build_bumper_canvas(
        result,
        final_message="Collision complete",
        autoplay=True,
        nonce=3,
    )
    assert '"id":"car_a"' in document
    assert '"id":"car_b"' in document
    assert '"id":"impact"' in document
    assert '"type":"particle_burst"' in document
    assert '"seed":20260713' in document
    assert "new AnimationPlayer(playerConfig,scene)" in document


def test_non_collision_canvas_has_no_impact_event() -> None:
    result = simulate_collision(CollisionParameters(2.0, 2.0, 1.0, 3.0, 1.0))
    document = build_bumper_canvas(
        result,
        final_message="No collision",
        autoplay=False,
        nonce=0,
    )
    assert '"events":[]' in document


def test_comparison_canvas_contains_two_runs_and_four_tracks() -> None:
    baseline = simulate_collision(CollisionParameters(2.0, 2.0, 4.0, 0.0, 1.0))
    modified = simulate_collision(CollisionParameters(2.0, 4.0, 4.0, 0.0, 1.0))
    document = build_bumper_comparison_canvas(
        baseline,
        modified,
        changed_variable="Car B mass",
        nonce=1,
        autoplay=True,
    )
    for track_id in ("run_a_car_a", "run_a_car_b", "run_b_car_a", "run_b_car_b"):
        assert f'"id":"{track_id}"' in document
    assert "Run A" in document
    assert "Run B" in document
