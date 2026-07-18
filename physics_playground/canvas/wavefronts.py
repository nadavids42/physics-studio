"""Reusable shared-player adapter for physically positioned sound wavefronts."""

from __future__ import annotations

from physics_playground.canvas.player import build_player_document
from physics_playground.frontend_assets import load_javascript_asset

SCENE = load_javascript_asset("scene-wavefronts.js")


def build_wavefront_document(
    *,
    frames: list[dict],
    world_min: float,
    world_max: float,
    duration_s: float,
    message: str,
    seed: int,
    autoplay: bool = False,
    source_velocity_m_s: float = 0,
    observer_velocity_m_s: float = 0,
    wavelength_ahead_m: float = 0,
    wavelength_behind_m: float = 0,
    motion_label: str = "Constant separation",
) -> str:
    config = {
        "durationMs": max(1200, int(duration_s * 2200)),
        "autoplay": autoplay,
        "seed": seed,
        "frameCount": len(frames),
        "tracks": [{"id": "clock", "label": "Wavefront time", "x": [0, 1]}],
        "events": [],
        "completionMessage": message,
        "wavefrontFrames": frames,
        "worldMin": world_min,
        "worldMax": world_max,
        "sourceVelocityMps": source_velocity_m_s,
        "observerVelocityMps": observer_velocity_m_s,
        "wavelengthAheadM": wavelength_ahead_m,
        "wavelengthBehindM": wavelength_behind_m,
        "motionLabel": motion_label,
        "view": {"minimum": 0, "maximum": 1},
    }
    return build_player_document(
        config=config,
        scene_javascript=SCENE,
        logical_width=820,
        logical_height=390,
        accessible_label="Animated sound wavefronts with physically positioned source, observer, emitted centers, and radii. "
        + message,
        idle_hint="Press Play or use frame-step controls to inspect the sound wavefronts",
    )
