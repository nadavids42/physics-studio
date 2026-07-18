"""Stable accessibility behavior exercised in a real browser when Chromium is available."""

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
from physics_playground.canvas.player import build_player_document


def _browser() -> str | None:
    return os.environ.get("CHROMIUM_BIN")


def test_player_keyboard_names_motion_and_responsive_behavior_in_chromium(tmp_path) -> None:
    browser = _browser()
    if not browser:
        pytest.skip("Chromium is required for browser accessibility verification.")
    configure_application_callbacks(
        ApplicationCallbacks(
            player_preferences=lambda: PlayerPreferences(
                reduced_motion=True,
                high_contrast=True,
                large_text=True,
                theme="light",
            )
        )
    )
    try:
        document = build_player_document(
            config={
                "durationMs": 1000,
                "autoplay": True,
                "tracks": [{"id": "body", "label": "Body", "x": [0, 1, 2]}],
                "events": [],
            },
            scene_javascript="const scene={draw(){}};",
            logical_width=680,
            logical_height=360,
            accessible_label="Projectile position over time",
            idle_hint="Play or step through the trajectory",
        )
    finally:
        reset_application_callbacks()
    audit = r"""
<script>
setTimeout(() => {
  const ids = ["play-pause","replay","step-back","step-forward","scrubber","speed"];
  const player = window.animationPlayer;
  const scrubber = document.getElementById("scrubber");
  const initial = {state: player.state, status: document.getElementById("status").textContent};
  document.getElementById("play-pause").click();
  document.getElementById("play-pause").click();
  document.getElementById("step-forward").click();
  const stepped = document.getElementById("status").textContent;
  scrubber.value = "750";
  scrubber.dispatchEvent(new Event("input", {bubbles:true}));
  scrubber.focus();
  const beforeSpace = player.state;
  scrubber.dispatchEvent(new KeyboardEvent("keydown", {key:" ", bubbles:true}));
  const result = {
    controlOrder: ids.map(id => document.getElementById(id).id),
    names: ids.map(id => document.getElementById(id).getAttribute("aria-label") || document.querySelector(`label[for=${id}]`)?.textContent),
    groupRole: document.querySelector(".controls").getAttribute("role"),
    canvasName: document.getElementById("animation-canvas").getAttribute("aria-label"),
    live: document.getElementById("status").getAttribute("aria-live"),
    initial,
    stepped,
    scrubberText: scrubber.getAttribute("aria-valuetext"),
    formSpacePreserved: player.state === beforeSpace,
    focusOutline: getComputedStyle(scrubber).outlineStyle,
    highContrast: document.body.classList.contains("high-contrast"),
    largeText: document.body.classList.contains("large-text"),
    reducedMotion: player.reducedMotion,
    noHorizontalOverflow: document.documentElement.scrollWidth <= document.documentElement.clientWidth,
  };
  const output = document.createElement("pre");
  output.id = "a11y-audit";
  output.textContent = JSON.stringify(result);
  document.body.appendChild(output);
}, 100);
</script>
"""
    path = tmp_path / "player-accessibility.html"
    path.write_text(document.replace("</body>", f"{audit}</body>"), encoding="utf-8")
    completed = subprocess.run(
        [
            browser,
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            "--no-sandbox",
            "--window-size=420,620",
            "--virtual-time-budget=1000",
            "--dump-dom",
            path.resolve().as_uri(),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    match = re.search(r'<pre id="a11y-audit">(.*?)</pre>', completed.stdout, re.DOTALL)
    assert match, completed.stderr
    result = json.loads(html.unescape(match.group(1)))
    assert result["controlOrder"] == [
        "play-pause",
        "replay",
        "step-back",
        "step-forward",
        "scrubber",
        "speed",
    ]
    assert all(result["names"])
    assert result["groupRole"] == "group"
    assert result["canvasName"] == "Projectile position over time"
    assert result["live"] == "polite"
    assert result["initial"]["state"] == "idle"
    assert "Reduced motion" in result["initial"]["status"]
    assert result["stepped"] == "Frame 2 of 3"
    assert result["scrubberText"] == "75 percent"
    assert result["formSpacePreserved"] is True
    assert result["focusOutline"] != "none"
    assert result["highContrast"] is True
    assert result["largeText"] is True
    assert result["reducedMotion"] is True
    assert result["noHorizontalOverflow"] is True
