"""Contract tests for the browser-side player document."""

import pytest

from physics_playground.canvas.player import build_player_document
from physics_playground.subjects.mechanics.bumper_cars.physics import (
    CollisionParameters,
    simulate_collision,
)
from physics_playground.subjects.mechanics.bumper_cars.scene import (
    build_bumper_canvas,
    build_bumper_comparison_canvas,
)


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
    assert "mountPhysicsPlayer(playerConfig,scene)" in document


@pytest.mark.parametrize(
    "config",
    ({"tracks": []}, {"durationMs": 1}, {"durationMs": 1, "tracks": [{"id": 1, "x": []}]}),
)
def test_python_rejects_malformed_player_payloads(config) -> None:
    with pytest.raises(ValueError):
        build_player_document(
            config=config,
            scene_javascript="const scene={draw(){}};",
            logical_width=100,
            logical_height=50,
            accessible_label="Malformed",
            idle_hint="Play",
        )


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
