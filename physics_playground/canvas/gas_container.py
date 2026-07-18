"""Reusable responsive piston animation for ideal-gas state comparisons."""

import random

from physics_playground.canvas.player import build_player_document
from physics_playground.frontend_assets import load_javascript_asset

SCENE = load_javascript_asset("scene-gas-container.js")


def build_gas_document(
    *,
    pressure_a_kpa: float,
    pressure_b_kpa: float,
    volume_a_m3: float,
    volume_b_m3: float,
    temp_a_k: float,
    temp_b_k: float,
    particles: int,
    message: str,
    seed: int,
    amount_mol: float = 1.0,
) -> str:
    rng = random.Random(seed)
    count = max(0, min(80, int(particles)))
    layout = [
        {
            "u": round(rng.random(), 8),
            "v": round(rng.random(), 8),
            "r": round(2.3 + rng.random() * 1.2, 4),
        }
        for _ in range(count)
    ]
    config = {
        "durationMs": 1700,
        "autoplay": False,
        "seed": seed,
        "tracks": [{"id": "gas-transition", "label": "Gas state transition", "x": [0, 1]}],
        "events": [],
        "completionMessage": message,
        "gasContainer": {
            "pressureA": pressure_a_kpa,
            "pressureB": pressure_b_kpa,
            "volumeA": volume_a_m3,
            "volumeB": volume_b_m3,
            "tempA": temp_a_k,
            "tempB": temp_b_k,
            "particles": count,
            "particleLayout": layout,
            "amount": amount_mol,
        },
        "view": {"minimum": 0, "maximum": 1},
    }
    return build_player_document(
        config=config,
        scene_javascript=SCENE,
        logical_width=720,
        logical_height=520,
        accessible_label="Gas piston changing from state A to state B. " + message,
        idle_hint="Press Play to animate the gas-state change",
    )
