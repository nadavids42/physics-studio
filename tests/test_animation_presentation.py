from copy import deepcopy
from pathlib import Path

from physics_playground.canvas.player import PLAYER_JS, build_player_document
from physics_playground.visual.animation import CANVAS_ANIMATION_JS


def _document(config=None):
    return build_player_document(
        config=config
        or {
            "durationMs": 1000,
            "tracks": [{"id": "x", "label": "x", "x": [0, 1, 2]}],
            "events": [],
        },
        scene_javascript="const scene={draw(){}};",
        logical_width=640,
        logical_height=320,
        accessible_label="Animation presentation",
        idle_hint="Play",
    )


def test_player_has_pause_resume_restart_stepping_speed_and_scrubbing_controls():
    document = _document()
    for token in (
        'id="play-pause"',
        'id="replay"',
        'id="step-back"',
        'id="step-forward"',
        'id="speed"',
        'id="scrubber"',
        "resume()",
        "stepFrames(amount)",
    ):
        assert token in document
    assert "Frame ${" in document


def test_player_uses_stable_display_timestep_raf_and_bounded_dpr():
    assert "requestAnimationFrame" in PLAYER_JS
    for token in ("fixedStep", "accumulator", "steps < 15", "maximumDpr", "devicePixelRatio"):
        assert token in PLAYER_JS


def test_player_cleans_up_browser_resources_and_does_not_add_stationary_trails():
    for token in (
        "resizeObserver?.disconnect",
        'removeEventListener("visibilitychange"',
        'removeEventListener("keydown"',
        "cancelAnimationFrame",
    ):
        assert token in PLAYER_JS
    assert "Math.abs(fraction - this.lastTrailFraction) > 1e-9" in PLAYER_JS


def test_animation_helpers_cover_camera_trails_blur_impacts_and_focus():
    for name in (
        "Camera",
        "withCamera",
        "fadingTrail",
        "subtleMotionBlur",
        "impactRipple",
        "collisionFlash",
        "focusTransition",
    ):
        assert name in CANVAS_ANIMATION_JS
    assert "this.reducedMotion ? 0" in CANVAS_ANIMATION_JS
    assert "if (options.reducedMotion) return" in CANVAS_ANIMATION_JS
    assert "Math.min(options.samples ?? 3, 4)" in CANVAS_ANIMATION_JS


def test_building_animation_document_does_not_mutate_physics_payload():
    config = {
        "durationMs": 1000,
        "tracks": [{"id": "body", "label": "Body", "x": [0.0, 1.0, 2.0], "y": [3.0, 4.0, 5.0]}],
        "events": [{"id": "impact", "fraction": 0.5}],
        "view": {"minimum": 0, "maximum": 2},
    }
    before = deepcopy(config)
    document = _document(config)
    assert config == before
    assert '"x":[0.0,1.0,2.0]' in document
    assert '"y":[3.0,4.0,5.0]' in document


def test_decorative_effects_are_presentation_only():
    source = (Path(__file__).parents[1] / "frontend/src/animation.js").read_text()
    assert "config.tracks" not in source
    assert "visualTokens" not in source
    assert "record" not in source.lower()
    assert "PhysicsAnimation" in _document()
