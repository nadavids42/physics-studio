"""Bounded shared-player renderer for seeded diffusion trajectories."""

from __future__ import annotations

from physics_playground.canvas.player import build_player_document
from physics_playground.frontend_assets import load_javascript_asset

VISIBLE_WINDOW_SEGMENTS = 48

SCENE = load_javascript_asset("scene-diffusion-player.js")


def build_diffusion_document(
    *,
    paths,
    dimensions: int,
    extent: float,
    message: str,
    seed: int,
    rms_distance_m: float = 0,
    sampled_particle_count: int | None = None,
) -> str:
    if dimensions not in (1, 2):
        raise ValueError("dimensions must be 1 or 2")
    immutable_paths = tuple(tuple(tuple(point) for point in path) for path in paths)
    extent = max(float(extent), 1e-9)
    config = {
        "durationMs": 2400,
        "autoplay": False,
        "seed": seed,
        "frameCount": max((len(path) for path in immutable_paths), default=2),
        "tracks": [{"id": "walks", "label": "Particle trajectories", "x": [0, 1]}],
        "events": [],
        "completionMessage": message,
        "diffusion": {
            "paths": immutable_paths,
            "dimensions": dimensions,
            "extent": extent,
            "rmsDistanceM": max(0, float(rms_distance_m)),
            "sampledParticleCount": sampled_particle_count or len(immutable_paths),
            "visibleWindowSegments": VISIBLE_WINDOW_SEGMENTS,
            "gridStepM": max(extent / 5, 1e-9),
        },
        "view": {"minimum": -extent, "maximum": extent},
    }
    label = (
        "1-dimensional random-walk trajectories constrained to the labeled horizontal axis. "
        if dimensions == 1
        else "2-dimensional random-walk trajectories on a labeled coordinate grid. "
    )
    return build_player_document(
        config=config,
        scene_javascript=SCENE,
        logical_width=760,
        logical_height=500,
        accessible_label=label
        + "Trajectories use numbered solid and dashed identities; the RMS guide describes the statistical distribution. "
        + message,
        idle_hint="Press Play or use frame-step controls to inspect the seeded walks",
    )
