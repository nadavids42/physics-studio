"""Shared-asset Double Pendulum animation adapter."""

from __future__ import annotations

from physics_playground.canvas.player import build_player_document
from physics_playground.frontend_assets import load_javascript_asset
from physics_playground.serialization import to_jsonable

CANVAS_W, CANVAS_H, PLAYER_HEIGHT = 560, 500, 590

SCENE = load_javascript_asset("scene-double-pendulum.js")


def build_double_canvas(
    r, *, seed, autoplay, show_separation: bool = True, inspect_system: str | None = None
):
    """Render synchronized recorded tracks with a fixed camera by default."""
    if inspect_system not in (None, "a", "b"):
        raise ValueError("inspect_system must be 'a', 'b', or None")
    tracks = [to_jsonable(track) for track in r.animation.tracks]
    limit = r.parameters.length_1_m + r.parameters.length_2_m
    config = {
        "durationMs": 6000,
        "autoplay": autoplay,
        "seed": seed,
        "trailLength": 72,
        "view": {"minimum": -limit, "maximum": limit},
        "limit": limit,
        "systems": ["a", "b"],
        "tracks": tracks,
        "events": [],
        "camera": {"x": 0, "y": 0, "zoom": 1},
        "doublePendulum": {
            "showSeparation": show_separation,
            "inspectSystem": inspect_system,
            "systems": [
                {"label": "Baseline A (solid)", "role": "accent", "lineStyle": "solid"},
                {"label": "Perturbed B (dashed)", "role": "energy", "lineStyle": "dashed"},
            ],
        },
        "completionMessage": "Chaos comparison complete",
    }
    return build_player_document(
        config=config,
        scene_javascript=SCENE,
        logical_width=CANVAS_W,
        logical_height=CANVAS_H,
        accessible_label="Baseline A with solid rods and perturbed B with dashed rods, evolving on one synchronized fixed-camera timeline.",
        idle_hint="Use Play or press RELEASE!",
    )
