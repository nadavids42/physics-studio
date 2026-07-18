"""Shared browser-player scene adapter for mechanics diagrams."""

from __future__ import annotations

from typing import Any

from physics_playground.canvas.player import build_player_document
from physics_playground.frontend_assets import load_javascript_asset

SCENE = load_javascript_asset("scene-mechanics.js")


def document(
    scene: str,
    tracks: list[dict[str, Any]],
    *,
    message: str,
    seed: int,
    autoplay: bool = True,
    scene_config: dict[str, Any] | None = None,
) -> str:
    """Build a mechanics scene while retaining the legacy call signature."""
    return build_player_document(
        config={
            "durationMs": 2200,
            "autoplay": autoplay,
            "seed": seed,
            "scene": scene,
            "mechanics": scene_config or {},
            "tracks": tracks,
            "events": [],
            "completionMessage": message,
            "view": {"minimum": 0, "maximum": 1},
        },
        scene_javascript=SCENE,
        logical_width=760,
        logical_height=360,
        accessible_label=f"{scene.title()} mechanics animation. {message}",
        idle_hint="Press Play to run the experiment",
    )
