"""Reusable browser-side player for precomputed simulation trajectories.

Each simulation supplies a JSON payload and a small scene adapter. This module
owns playback state, interpolation, controls, events, trails, particles,
responsive/high-DPI canvas setup, accessibility, and deterministic randomness.
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from physics_playground.application_callbacks import get_player_preferences
from physics_playground.frontend_assets import load_javascript_asset
from physics_playground.visual.css import shared_css
from physics_playground.visual.tokens import DARK_THEME, LIGHT_THEME, theme_payload

PLAYER_CSS = r"""
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: transparent; color: var(--ps-text);
  font-family: var(--ps-font-ui); }
.animation-shell { width: 100%; max-width: 900px; margin: 0 auto; }
.canvas-wrap { position: relative; width: 100%; aspect-ratio: var(--aspect-ratio);
  min-height: 180px; overflow: hidden; border-radius: 18px; }
canvas { display: block; width: 100%; max-width: 100%; height: 100%; }
.hint { position: absolute; left: 50%; top: 12px; transform: translateX(-50%);
  color: var(--ps-text-muted); font-size: 13px; font-weight: 600; pointer-events: none; }
.message { position: absolute; left: 50%; bottom: 12px; transform: translate(-50%, 6px);
  max-width: 88%; padding: 9px 16px; border-radius: var(--ps-radius-lg); background: var(--ps-surface-raised);
  color: var(--ps-text); box-shadow: var(--ps-shadow-medium); text-align: center;
  font-size: 14px; font-weight: 650; opacity: 0; transition: .25s ease; pointer-events: none; }
.message.show { opacity: 1; transform: translate(-50%, 0); }
.controls { display: grid; grid-template-columns: auto auto auto auto minmax(100px,1fr) auto;
  gap: 8px; align-items: center; padding: 8px 2px 0; }
.controls button, .controls select { min-height: 44px; border: 1px solid var(--ps-border);
  border-radius: var(--ps-radius-md); background: var(--ps-surface); color: var(--ps-text); font-weight: 650; cursor: pointer; }
.controls button { min-width: 42px; padding: 5px 10px; }
.controls button:focus-visible, .controls select:focus-visible, .controls input:focus-visible {
  outline: 3px solid var(--ps-focus); outline-offset: 2px; }
.controls input[type=range] { width: 100%; accent-color: var(--ps-accent); }
.speed-label { display: flex; align-items: center; gap: 5px; font-size: 12px; white-space: nowrap; }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
  overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }
@media (max-width: 480px) {
  .controls { grid-template-columns: repeat(4,auto) minmax(80px,1fr); }
  .speed-label { grid-column: 1 / -1; justify-content: flex-end; }
  .controls button { min-width: 38px; padding-inline: 7px; }
}
@media (prefers-reduced-motion: reduce) {
  .message { transition: none; }
}
body.large-text .hint, body.large-text .speed-label { font-size: 15px; }
body.large-text .message { font-size: 17px; }
body.large-text .controls button, body.large-text .controls select { font-size: 17px; min-height: 48px; }
body.high-contrast .canvas-wrap { outline: 3px solid #fff; background:#000; }
body.high-contrast .controls button, body.high-contrast .controls select { background:#000; color:#fff; border:2px solid #fff; }
body.high-contrast .controls input[type=range] { accent-color:#FFD600; }
"""

PLAYER_JS = load_javascript_asset("player-runtime.js")


def _validate_player_config(config: dict[str, Any]) -> None:
    """Validate the stable Python-to-browser player payload boundary."""

    duration_ms = config.get("durationMs")
    if (
        not isinstance(duration_ms, int | float)
        or isinstance(duration_ms, bool)
        or duration_ms <= 0
    ):
        raise ValueError("Player config requires a positive numeric durationMs.")
    tracks = config.get("tracks")
    if not isinstance(tracks, list):
        raise ValueError("Player config requires a tracks list.")
    for track in tracks:
        if not isinstance(track, dict) or not isinstance(track.get("id"), str):
            raise ValueError("Each player track requires a string id.")
        if not isinstance(track.get("x"), list):
            raise ValueError("Each player track requires an x list.")


def build_player_document(
    *,
    config: dict[str, Any],
    scene_javascript: str,
    logical_width: int,
    logical_height: int,
    accessible_label: str,
    idle_hint: str,
    extra_css: str = "",
) -> str:
    """Build a standalone responsive player document for Streamlit embedding."""

    _validate_player_config(config)
    config = {
        **config,
        "visualThemes": {"light": theme_payload(LIGHT_THEME), "dark": theme_payload(DARK_THEME)},
        "theme": config.get("theme", "auto"),
    }
    preferences = get_player_preferences()
    config = {
        **config,
        "reducedMotion": preferences.reduced_motion,
        "highContrast": preferences.high_contrast,
        "largeText": preferences.large_text,
        "presentationLevel": config.get("presentationLevel", preferences.presentation_level),
        "theme": config.get("theme", preferences.theme),
    }
    payload = json.dumps(config, allow_nan=False, separators=(",", ":"))
    aspect_ratio = logical_width / logical_height
    return _cached_player_document(
        payload, scene_javascript, aspect_ratio, accessible_label, idle_hint, extra_css
    )


@lru_cache(maxsize=128)
def _cached_player_document(
    payload: str,
    scene_javascript: str,
    aspect_ratio: float,
    accessible_label: str,
    idle_hint: str,
    extra_css: str,
) -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>:root{{--aspect-ratio:{aspect_ratio};}}{shared_css()}{PLAYER_CSS}{extra_css}</style></head>
<body><div class="animation-shell" role="group" aria-label={json.dumps(accessible_label)}>
  <div class="canvas-wrap" id="canvas-wrap"><canvas id="animation-canvas" role="img" aria-label={json.dumps(accessible_label)}></canvas>
    <div class="hint" id="hint">{idle_hint}</div><div class="message" id="message" aria-live="polite"></div></div>
  <div class="controls" aria-label="Animation controls">
    <button id="play-pause" type="button" aria-label="Play animation" title="Play or pause (Space)">▶</button>
    <button id="replay" type="button" aria-label="Replay animation" title="Replay (R)">↺</button>
    <button id="step-back" type="button" aria-label="Step backward one frame" title="Previous frame (,)">‹</button>
    <button id="step-forward" type="button" aria-label="Step forward one frame" title="Next frame (.)">›</button>
    <label class="sr-only" for="scrubber">Animation position</label><input id="scrubber" type="range" min="0" max="1000" value="0">
    <label class="speed-label" for="speed">Speed <select id="speed"><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="1.5">1.5×</option><option value="2">2×</option></select></label>
  </div><div id="status" class="sr-only" aria-live="polite">Animation ready</div></div>
<script>{PLAYER_JS}\nconst playerConfig={payload};\n{scene_javascript}\nwindow.animationPlayer=mountPhysicsPlayer(playerConfig,scene);</script>
</body></html>"""


def player_document_cache_info():
    return _cached_player_document.cache_info()
