"""Swing Machine scene adapters for the shared player."""

from physics_playground.canvas.player import build_player_document
from physics_playground.frontend_assets import load_javascript_asset
from physics_playground.serialization import to_jsonable

CANVAS_W, CANVAS_H, PLAYER_HEIGHT = 500, 440, 520
SCENE = load_javascript_asset("scene-pendulum.js")


def _doc(items, seed, autoplay, message):
    tracks = []
    for i, (label, r, color) in enumerate(items):
        q = to_jsonable(r.animation.tracks[0])
        q["id"] = f"bob_{i}"
        q["label"] = label
        q["style"] = {"color": color}
        tracks.append(q)
    config = {
        "durationMs": 4800,
        "autoplay": autoplay,
        "seed": seed,
        "trailLength": 18,
        "view": {"minimum": -1, "maximum": 1},
        "maxLength": max(r.parameters.length_m for _, r, _ in items),
        "tracks": tracks,
        "events": [],
        "completionMessage": message,
    }
    return build_player_document(
        config=config,
        scene_javascript=SCENE,
        logical_width=CANVAS_W,
        logical_height=CANVAS_H,
        accessible_label="Pendulum bob motion with rope length shown to scale.",
        idle_hint="Use Play or press SWING!",
    )


def build_pendulum_canvas(r, *, seed, autoplay):
    return _doc([("Pendulum", r, "#66BB6A")], seed, autoplay, "Swing complete")


def build_pendulum_comparison_canvas(a, b, *, labels, seed, autoplay):
    return _doc(
        [(labels[0], a, "#1565C0"), (labels[1], b, "#E65100")],
        seed,
        autoplay,
        "Comparison complete",
    )
