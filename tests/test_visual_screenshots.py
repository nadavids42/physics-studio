"""Small perceptual regression suite rendered by a real browser.

The baselines in ``visual_baselines.json`` were captured with Chromium
141.0.7390.37 (the Playwright-managed build at revision 1194, e.g.
``/opt/pw-browsers/chromium-1194/chrome-linux/chrome``). Perceptual hashes are
not stable across different Chromium builds/versions — font hinting, control
sizing, and canvas rasterization all shift enough to move the dhash distance
well past the comparison threshold even though the rendering is correct. If
this suite fails against a browser whose ``--version`` output differs from
the one above, recapture rather than loosen the threshold further: point
``CHROMIUM_BIN`` at that exact build and run
``CHROMIUM_BIN=/path/to/chromium PHYSICS_UPDATE_VISUAL_BASELINES=1 pytest
tests/test_visual_screenshots.py`` once (it intentionally fails after writing
so the diff gets reviewed), inspect the rendered PNGs in the pytest tmp
directory to confirm nothing is actually broken, then commit the updated
``visual_baselines.json`` alongside a note of the new pinned build.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

import pytest
from PIL import Image, ImageStat

from physics_playground.application_callbacks import (
    ApplicationCallbacks,
    PlayerPreferences,
    configure_application_callbacks,
    reset_application_callbacks,
)
from physics_playground.canvas.player import build_player_document
from physics_playground.canvas.ray_diagram import SCENE as RAY_SCENE
from physics_playground.subjects.mechanics.cannonball.scene import SCENE as CANNON_SCENE
from physics_playground.subjects.mechanics.canvas import SCENE as MECHANICS_SCENE
from physics_playground.subjects.mechanics.inclined_plane.physics import (
    InclinedPlaneParameters,
    simulate,
)
from physics_playground.subjects.mechanics.inclined_plane.visuals import force_vectors
from physics_playground.subjects.waves_and_oscillations.pendulum.scene import (
    SCENE as PENDULUM_SCENE,
)

BASELINES = Path(__file__).with_name("visual_baselines.json")

INCLINED_RESULT = simulate(
    InclinedPlaneParameters(
        mass_kg=2,
        angle_deg=35,
        static_friction=0.4,
        kinetic_friction=0.25,
    )
)
INCLINED_VECTORS, INCLINED_SCALE = force_vectors(INCLINED_RESULT)


@dataclass(frozen=True)
class Fingerprint:
    dhash: str
    mean_rgb: tuple[float, float, float]


def _base_config(**extra):
    return {
        "durationMs": 1000,
        "autoplay": False,
        "seed": 17,
        "tracks": [],
        "events": [],
        **extra,
    }


CASES = {
    "inclined-force-scale-light": (
        MECHANICS_SCENE,
        _base_config(
            theme="light",
            scene="ramp",
            mechanics={
                "angleDeg": 35,
                "criticalAngleDeg": INCLINED_RESULT.critical_angle_deg,
                "moving": INCLINED_RESULT.moving,
                "motionState": "sliding",
                "frictionState": "kinetic friction",
                "staticFrictionLimitN": (
                    INCLINED_RESULT.parameters.static_friction * INCLINED_RESULT.normal_force_n
                ),
                "forceScalePxPerN": INCLINED_SCALE,
                "vectors": INCLINED_VECTORS,
            },
            tracks=[{"id": "block", "label": "Block", "x": [0.35]}],
        ),
        PlayerPreferences(theme="light"),
        (900, 560),
    ),
    "mechanics-light": (
        CANNON_SCENE,
        _base_config(
            theme="light",
            angle=45,
            target=8,
            view={"xMin": 0, "xMax": 10, "yMin": 0, "yMax": 5},
            tracks=[{"id": "projectile", "label": "Ball", "x": [2], "y": [1]}],
        ),
        PlayerPreferences(theme="light"),
        (900, 560),
    ),
    "pendulum-dark": (
        PENDULUM_SCENE,
        _base_config(
            theme="dark",
            maxLength=2,
            tracks=[{"id": "bob", "label": "Bob", "x": [0.6], "y": [-1.8]}],
        ),
        PlayerPreferences(theme="dark"),
        (700, 650),
    ),
    "optics-high-contrast": (
        RAY_SCENE,
        _base_config(
            theme="light",
            rayConfig={
                "rays": [{"x1": -4, "y1": 1.5, "x2": 4, "y2": -1, "label": "Principal"}],
                "lens": True,
                "lensSign": 1,
                "xmin": -5,
                "xmax": 5,
                "ymin": -3,
                "ymax": 3,
            },
            tracks=[{"id": "ray-progress", "x": [0, 1]}],
        ),
        PlayerPreferences(high_contrast=True, theme="light"),
        (900, 560),
    ),
    "mechanics-reduced-mobile": (
        CANNON_SCENE,
        _base_config(
            theme="light",
            angle=35,
            target=6,
            view={"xMin": 0, "xMax": 8, "yMin": 0, "yMax": 4},
            tracks=[{"id": "projectile", "label": "Ball", "x": [2], "y": [1]}],
        ),
        PlayerPreferences(reduced_motion=True, theme="light"),
        (420, 620),
    ),
    "optics-dark-mobile": (
        RAY_SCENE,
        _base_config(
            theme="dark",
            rayConfig={
                "rays": [{"x1": -4, "y1": 1, "x2": 4, "y2": -1}],
                "lens": True,
                "lensSign": -1,
                "xmin": -5,
                "xmax": 5,
                "ymin": -3,
                "ymax": 3,
            },
            tracks=[{"id": "ray-progress", "x": [0, 1]}],
        ),
        PlayerPreferences(theme="dark"),
        (420, 620),
    ),
}


def _fingerprint(path: Path) -> Fingerprint:
    with Image.open(path).convert("RGB") as image:
        gray = image.convert("L").resize((17, 16))
        pixels = list(gray.tobytes())
        bits = []
        for row in range(16):
            offset = row * 17
            bits.extend(
                pixels[offset + column] > pixels[offset + column + 1] for column in range(16)
            )
        value = sum(int(bit) << index for index, bit in enumerate(bits))
        means = tuple(round(value, 2) for value in ImageStat.Stat(image).mean[:3])
    return Fingerprint(f"{value:064x}", means)


def _distance(left: str, right: str) -> int:
    return (int(left, 16) ^ int(right, 16)).bit_count()


def _render(case, destination: Path, browser: str) -> Fingerprint:
    scene, config, preferences, viewport = case
    configure_application_callbacks(ApplicationCallbacks(player_preferences=lambda: preferences))
    try:
        document = build_player_document(
            config=config,
            scene_javascript=scene,
            logical_width=680,
            logical_height=360,
            accessible_label="Visual regression scene",
            idle_hint="Play",
        )
    finally:
        reset_application_callbacks()
    html = destination.with_suffix(".html")
    html.write_text(document, encoding="utf-8")
    subprocess.run(
        [
            browser,
            "--headless",
            "--disable-gpu",
            "--hide-scrollbars",
            "--no-sandbox",
            f"--window-size={viewport[0]},{viewport[1]}",
            f"--screenshot={destination}",
            html.resolve().as_uri(),
        ],
        check=True,
        capture_output=True,
        timeout=30,
    )
    return _fingerprint(destination)


@pytest.mark.skipif(
    not os.environ.get("CHROMIUM_BIN"),
    reason="SKIPPED: browser tests require CHROMIUM_BIN; this run has NO browser coverage.",
)
def test_representative_browser_renderings(tmp_path) -> None:
    browser = os.environ["CHROMIUM_BIN"]
    expected = json.loads(BASELINES.read_text(encoding="utf-8"))
    actual = {
        name: asdict(_render(case, tmp_path / f"{name}.png", browser))
        for name, case in CASES.items()
    }
    if os.environ.get("PHYSICS_UPDATE_VISUAL_BASELINES") == "1":
        BASELINES.write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        pytest.fail("Visual baselines updated; inspect and rerun without update mode.")
    assert set(actual) == set(expected)
    failures = []
    for name, current in actual.items():
        baseline = expected[name]
        dhash_distance = _distance(current["dhash"], baseline["dhash"])
        rgb_distance = max(
            abs(current_value - baseline_value)
            for current_value, baseline_value in zip(
                current["mean_rgb"], baseline["mean_rgb"], strict=True
            )
        )
        if dhash_distance > 12 or rgb_distance > 8:
            failures.append(f"{name}: dhash_distance={dhash_distance} rgb_distance={rgb_distance}")
    assert not failures, "\n".join(failures)
