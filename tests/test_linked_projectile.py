"""Payload, accessibility, performance, and cache tests for the linked pilot."""

from __future__ import annotations

import html
import json
import os
import re
import subprocess

import pytest

from physics_playground.application_callbacks import (
    ApplicationCallbacks,
    PlayerPreferences,
    configure_application_callbacks,
    reset_application_callbacks,
)
from physics_playground.subjects.mechanics.cannonball.linked_representations import (
    LINKED_JS,
    build_linked_projectile_document,
    linked_document_cache_info,
    linked_projectile_payload,
)
from physics_playground.subjects.mechanics.cannonball.physics import (
    ProjectileParameters,
    simulate_no_drag,
)


def _result(angle: float = 45.0):
    return simulate_no_drag(ProjectileParameters(20.0, angle, samples=120))


def test_payload_is_derived_from_result_samples_and_has_vector_units() -> None:
    result = _result()
    payload = linked_projectile_payload((("Run A", result),), target_m=30.0)
    run = payload["representations"]["runs"][0]
    assert run["time_s"][0] == result.animation.time_s[0]
    assert run["time_s"][-1] == result.animation.time_s[-1]
    assert run["x_m"][0] == result.animation.tracks[0].x[0]
    assert run["x_m"][-1] == result.animation.tracks[0].x[-1]
    assert len(run["vx_m_s"]) == len(result.animation.time_s)
    assert len(run["ay_m_s2"]) == len(result.animation.time_s)
    assert abs(run["ay_m_s2"][len(run["ay_m_s2"]) // 2] + 9.81) < 0.05


def test_comparison_document_is_one_runtime_with_shared_axes_and_stable_cache() -> None:
    results = (("30 degrees", _result(30)), ("60 degrees", _result(60)))
    before = linked_document_cache_info()
    first = build_linked_projectile_document(results, target_m=40.0)
    second = build_linked_projectile_document(results, target_m=40.0)
    after = linked_document_cache_info()
    assert first == second and after.hits > before.hits
    assert first.count("<iframe") == 0
    assert first.count("mountLinkedProjectile") >= 1
    assert 'class="linked-graph"' in first
    payload = linked_projectile_payload(results, target_m=40.0)
    assert len(payload["representations"]["runs"]) == 2
    assert payload["view"]["xMax"] > max(result.range_m for _, result in results)


def test_accessible_controls_equations_and_reduced_motion_are_in_same_document() -> None:
    configure_application_callbacks(
        ApplicationCallbacks(player_preferences=lambda: PlayerPreferences(reduced_motion=True))
    )
    try:
        document = build_linked_projectile_document((("Run A", _result()),))
    finally:
        reset_application_callbacks()
    assert '"reducedMotion":true' in document
    assert 'aria-label="Linked representation controls"' in document
    assert 'id="linked-readout" aria-live="off"' in document
    assert 'id="linked-announcement" class="sr-only" role="status" aria-live="polite"' in document
    assert "Horizontal: short/solid pattern" in document
    assert "@media(forced-colors:active)" in document
    assert document.count('class="linked-graph"') == 3
    assert document.count('tabindex="0"') == 3
    assert document.count('class="equation-term"') == 4


def test_bundle_and_typical_payload_are_bounded() -> None:
    payload_bytes = len(json.dumps(linked_projectile_payload((("Run A", _result()),))).encode())
    assert len(LINKED_JS.encode()) < 90_000
    assert payload_bytes < 50_000


@pytest.mark.skipif(
    not os.environ.get("CHROMIUM_BIN"),
    reason="SKIPPED: browser tests require CHROMIUM_BIN; this run has NO browser coverage.",
)
def test_linked_runtime_keyboard_accessibility_and_frame_time_in_chromium(tmp_path) -> None:
    browser = os.environ["CHROMIUM_BIN"]
    document = build_linked_projectile_document((("Run A", _result(30)), ("Run B", _result(60))))
    audit = """
<script>setTimeout(()=>{const runtime=window.linkedProjectile;const graph=document.querySelector('.linked-graph');
const start=performance.now();for(let i=0;i<100;i++)runtime.player.seek(i/99);const elapsed=performance.now()-start;
graph.dispatchEvent(new KeyboardEvent('keydown',{key:'Home',bubbles:true}));
graph.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));
document.querySelector('[data-quantity=velocity]').click();const patterns=[...document.querySelectorAll('.quantity-line')].map(node=>getComputedStyle(node).strokeDasharray);
const result={averageSeekMs:elapsed/100,fraction:runtime.player.fraction,readout:document.getElementById('linked-readout').textContent,
graphLabel:graph.getAttribute('aria-label'),highlight:document.body.dataset.highlightQuantity,reduced:runtime.player.reducedMotion,
singleCanvas:document.querySelectorAll('canvas').length,singleClock:Boolean(runtime.player),noOverflow:document.documentElement.scrollWidth<=document.documentElement.clientWidth,
forcedColors:matchMedia('(forced-colors: active)').matches,patterns:[...new Set(patterns)]};runtime.destroy();result.destroyed=runtime.destroyed;
const out=document.createElement('pre');out.id='linked-audit';out.textContent=JSON.stringify(result);document.body.append(out)},150);</script>
"""
    path = tmp_path / "linked-projectile.html"
    path.write_text(document.replace("</body>", f"{audit}</body>"), encoding="utf-8")
    completed = subprocess.run(
        [
            browser,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--virtual-time-budget=1200",
            "--window-size=320,1000",
            "--force-high-contrast",
            "--dump-dom",
            path.resolve().as_uri(),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    match = re.search(r'<pre id="linked-audit">(.*?)</pre>', completed.stdout, re.DOTALL)
    assert match, completed.stderr
    result = json.loads(html.unescape(match.group(1)))
    assert result["averageSeekMs"] < 16.7
    assert result["fraction"] > 0
    assert "position x" in result["readout"] and "acceleration ax" in result["readout"]
    assert result["graphLabel"] and result["highlight"] == "velocity"
    assert result["singleCanvas"] == 1 and result["singleClock"] is True
    assert result["noOverflow"] is True and result["forcedColors"] is True
    assert len(result["patterns"]) >= 3
    assert result["destroyed"] is True
