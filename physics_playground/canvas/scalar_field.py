"""Reusable scientific graph-plane adapter for precomputed scalar fields."""

from __future__ import annotations

from physics_playground.canvas.player import build_player_document
from physics_playground.frontend_assets import load_javascript_asset

SCENE = load_javascript_asset("scene-scalar-field.js")


def build_scalar_field_document(
    *,
    x: tuple[float, ...],
    frames: tuple[tuple[float, ...], ...],
    duration_s: float,
    accessible_label: str,
    completion_message: str,
    seed: int,
    autoplay: bool = False,
    source_frames: tuple[tuple[tuple[float, ...], ...], ...] = (),
    sources: tuple[dict, ...] = (),
    measurements: tuple[dict, ...] = (),
    time_s: tuple[float, ...] = (),
    interference_label: str = "",
) -> str:
    """Build a fixed-scale graph whose curves are the supplied recorded samples."""
    theoretical_limit = sum(abs(float(source.get("amplitude", 0))) for source in sources)
    recorded_limit = max((abs(value) for frame in frames for value in frame), default=1.0)
    limit = max(1e-6, theoretical_limit, recorded_limit)
    times = time_s or tuple(duration_s * i / max(1, len(frames) - 1) for i in range(len(frames)))
    config = {
        "durationMs": max(1000, int(duration_s * 2500)),
        "fieldDurationS": duration_s,
        "autoplay": autoplay,
        "seed": seed,
        "frameCount": len(frames),
        "tracks": [{"id": "field-clock", "label": "Wave field", "x": [0, 1]}],
        "events": [],
        "completionMessage": completion_message,
        "fieldX": x,
        "fieldFrames": frames,
        "sourceFrames": source_frames,
        "sources": sources,
        "measurements": measurements,
        "fieldTimes": times,
        "interferenceLabel": interference_label,
        "fieldLimit": limit,
        "view": {"minimum": 0, "maximum": 1},
    }
    return build_player_document(
        config=config,
        scene_javascript=SCENE,
        logical_width=820,
        logical_height=390,
        accessible_label=accessible_label,
        idle_hint="Press Play or use frame-step controls to inspect the field",
    )
