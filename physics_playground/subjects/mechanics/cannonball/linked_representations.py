"""Single-document linked projectile representations derived from model results."""

from __future__ import annotations

import json
from functools import lru_cache

import numpy as np

from physics_playground.application_callbacks import get_player_preferences
from physics_playground.canvas.player import PLAYER_CSS
from physics_playground.frontend_assets import load_javascript_asset
from physics_playground.frontend_protocol import linked_projectile_envelope
from physics_playground.serialization import to_jsonable
from physics_playground.subjects.mechanics.cannonball.physics import ProjectileResult
from physics_playground.visual.css import shared_css
from physics_playground.visual.tokens import DARK_THEME, LIGHT_THEME, theme_payload

LINKED_JS = load_javascript_asset("linked-projectile.js")
LINKED_HEIGHT = 1080
RUN_COLORS = ("#37474F", "#7B1FA2")
MAX_LINKED_SAMPLES = 120

LINKED_CSS = """
.linked-shell{max-width:960px;margin:auto}.linked-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.linked-graph{width:100%;height:auto;border:1px solid var(--ps-border);border-radius:10px;background:var(--ps-surface)}
.quantity-line{fill:none;stroke-width:2.5}.quantity-line.horizontal{stroke:#6F4E7C}.quantity-line.vertical{stroke:#C43C39;stroke-dasharray:3 3}
.quantity-line.horizontal.run-1{stroke-dasharray:10 4}.quantity-line.vertical.run-1{stroke-dasharray:10 3 2 3}.zero{stroke:var(--ps-border)}.graph-cursor{stroke:#111;stroke-width:2}
.graph-title{fill:var(--ps-text);font-weight:700;font-size:13px}.equations{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}
.equation-term{min-height:44px;border:2px solid var(--ps-border);border-radius:8px;background:var(--ps-surface);color:var(--ps-text);padding:7px 12px;font-family:serif;font-size:16px}
.equation-term:focus-visible,.linked-graph:focus-visible{outline:3px solid var(--ps-focus);outline-offset:2px}
#linked-readout{border-left:4px solid #0072B2;padding:8px 12px;margin:8px 0;background:var(--ps-surface-raised)}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-weight:650}.horizontal-label{color:#6F4E7C}.vertical-label{color:#C43C39}
body[data-highlight-quantity=position] [data-quantity]:not([data-quantity=position]),body[data-highlight-quantity=velocity] [data-quantity]:not([data-quantity=velocity]),body[data-highlight-quantity=acceleration] [data-quantity]:not([data-quantity=acceleration]){opacity:.22}
@media(max-width:680px){.linked-grid{grid-template-columns:1fr}.equation-term{width:100%}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}
@media(forced-colors:active){.quantity-line{stroke:CanvasText!important}.graph-cursor{stroke:Highlight!important;stroke-width:3}.linked-graph{border-color:CanvasText}.equation-term:focus-visible,.linked-graph:focus-visible{outline-color:Highlight}}
"""


def _run_payload(result: ProjectileResult, label: str) -> dict[str, object]:
    track = result.animation.tracks[0]
    time_s = np.asarray(result.animation.time_s, dtype=float)
    x_m = np.asarray(track.x, dtype=float)
    y_m = np.asarray(track.y, dtype=float)
    if len(time_s) > MAX_LINKED_SAMPLES:
        indices = np.linspace(0, len(time_s) - 1, MAX_LINKED_SAMPLES, dtype=int)
        time_s, x_m, y_m = time_s[indices], x_m[indices], y_m[indices]
    edge_order = 2 if len(time_s) > 2 else 1
    vx = np.gradient(x_m, time_s, edge_order=edge_order)
    vy = np.gradient(y_m, time_s, edge_order=edge_order)
    ax = np.gradient(vx, time_s, edge_order=edge_order)
    ay = np.gradient(vy, time_s, edge_order=edge_order)
    return {
        "label": label,
        "time_s": to_jsonable(time_s),
        "x_m": to_jsonable(x_m),
        "y_m": to_jsonable(y_m),
        "vx_m_s": to_jsonable(vx),
        "vy_m_s": to_jsonable(vy),
        "ax_m_s2": to_jsonable(ax),
        "ay_m_s2": to_jsonable(ay),
    }


def linked_projectile_payload(
    results: tuple[tuple[str, ProjectileResult], ...], *, target_m: float = 0.0
) -> dict[str, object]:
    """Build one shared-clock payload exclusively from Python result samples."""

    if not results:
        raise ValueError("Linked representations require at least one result.")
    x_max = max(target_m, *(result.range_m for _, result in results)) * 1.15 + 3
    y_max = max(result.maximum_height_m for _, result in results) * 1.25 + 1
    tracks = []
    runs = []
    for index, (label, result) in enumerate(results):
        run = _run_payload(result, label)
        track = {
            "x": run["x_m"],
            "y": run["y_m"],
        }
        track["id"] = f"projectile_{index}"
        track["label"] = label
        track["style"] = {"color": RUN_COLORS[index % len(RUN_COLORS)]}
        tracks.append(track)
        runs.append(run)
    return {
        "durationMs": 3_200,
        "autoplay": False,
        "frameCount": max(len(result.animation.time_s) for _, result in results),
        "tracks": tracks,
        "events": [],
        "view": {"xMin": 0.0, "xMax": x_max, "yMin": 0.0, "yMax": y_max},
        "target": target_m,
        "angle": results[0][1].parameters.launch_angle_deg,
        "representations": {"runs": runs},
        "visualThemes": {
            "light": theme_payload(LIGHT_THEME),
            "dark": theme_payload(DARK_THEME),
        },
        "theme": "auto",
    }


def build_linked_projectile_document(
    results: tuple[tuple[str, ProjectileResult], ...], *, target_m: float = 0.0
) -> str:
    preferences = get_player_preferences()
    config = {
        **linked_projectile_payload(results, target_m=target_m),
        "reducedMotion": preferences.reduced_motion,
        "highContrast": preferences.high_contrast,
        "largeText": preferences.large_text,
        "theme": preferences.theme,
    }
    model_versions = {result.model_version for _, result in results}
    if len(model_versions) != 1:
        raise ValueError("Linked comparison runs must use one model version.")
    envelope = linked_projectile_envelope(
        simulation_id="cannonball",
        model_version=model_versions.pop(),
        payload=config,
    )
    payload = json.dumps(
        envelope,
        allow_nan=False,
        separators=(",", ":"),
    )
    return _document(payload)


@lru_cache(maxsize=32)
def _document(payload: str) -> str:
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>:root{{--aspect-ratio:1.89}}{shared_css()}{PLAYER_CSS}{LINKED_CSS}</style></head><body>
<main class="linked-shell" aria-label="Linked projectile representations">
<div class="animation-shell"><div class="canvas-wrap" id="canvas-wrap"><canvas id="animation-canvas" role="img" aria-label="Projectile position and trajectory synchronized with motion graphs"></canvas><div class="hint" id="hint">Scrub, step, or select a graph point</div><div class="message" id="message" aria-live="polite"></div></div>
<div class="controls" role="group" aria-label="Linked representation controls"><button id="play-pause" aria-label="Play animation">▶</button><button id="replay" aria-label="Replay animation">↺</button><button id="step-back" aria-label="Step backward one sample">‹</button><button id="step-forward" aria-label="Step forward one sample">›</button><label class="sr-only" for="scrubber">Time and linked graph position</label><input id="scrubber" type="range" min="0" max="1000" value="0"><label class="speed-label" for="speed">Speed <select id="speed"><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option></select></label></div><div id="status" class="sr-only" aria-live="polite">Linked representations ready</div></div>
<p class="legend"><span class="horizontal-label">Horizontal: short/solid pattern</span><span class="vertical-label">Vertical: dotted/compound pattern</span><span>Run A: shorter pattern</span><span>Run B: longer pattern</span></p>
<div id="linked-readout" aria-live="off"></div><div id="linked-announcement" class="sr-only" role="status" aria-live="polite"></div>
<section class="equations" aria-label="Governing equations; select a term to highlight its representation">
<button class="equation-term" data-quantity="position">x(t)=x₀+vₓt</button><button class="equation-term" data-quantity="position">y(t)=y₀+vᵧ₀t−½gt²</button><button class="equation-term" data-quantity="velocity">vᵧ(t)=vᵧ₀−gt</button><button class="equation-term" data-quantity="acceleration">a=(0,−g)</button></section>
<div class="linked-grid"><svg class="linked-graph" data-quantity="position" viewBox="0 0 420 190" tabindex="0"></svg><svg class="linked-graph" data-quantity="velocity" viewBox="0 0 420 190" tabindex="0"></svg><svg class="linked-graph" data-quantity="acceleration" viewBox="0 0 420 190" tabindex="0"></svg></div>
</main><script>{LINKED_JS}\nconst frontendEnvelope={payload};window.linkedProjectile=mountLinkedProjectile(frontendEnvelope);</script></body></html>"""


def linked_document_cache_info() -> object:
    return _document.cache_info()
