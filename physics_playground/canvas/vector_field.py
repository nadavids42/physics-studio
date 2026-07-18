"""Reusable bounded vector-field and scalar-potential diagram renderer."""

import math

from physics_playground.canvas.player import build_player_document
from physics_playground.frontend_assets import load_javascript_asset

SCENE = load_javascript_asset("scene-vector-field.js")


def build_vector_field_document(
    *,
    samples: list[dict],
    charges: list[dict],
    grid_size: int,
    extent: float,
    test_x: float,
    test_y: float,
    message: str,
    seed: int,
    test_charge: float = 1.0,
) -> str:
    finite = [
        item
        for item in samples
        if item.get("v") is not None and item.get("ex") is not None and item.get("ey") is not None
    ]
    excluded = [{"x": item["x"], "y": item["y"]} for item in samples if item.get("v") is None]
    potential_limit = max((abs(float(item["v"])) for item in finite), default=1.0) or 1.0
    field_limit = (
        max((math.hypot(float(item["ex"]), float(item["ey"])) for item in finite), default=1.0)
        or 1.0
    )
    config = {
        "durationMs": 1600,
        "autoplay": False,
        "seed": seed,
        "tracks": [{"id": "field-reveal", "label": "Electric field reveal", "x": [0, 1]}],
        "events": [],
        "completionMessage": message,
        "vectorField": {
            "samples": finite,
            "excluded": excluded,
            "charges": charges,
            "gridSize": grid_size,
            "extent": extent,
            "testX": test_x,
            "testY": test_y,
            "testCharge": test_charge,
            "potentialLimit": potential_limit,
            "fieldMagnitudeLimit": field_limit,
        },
        "view": {"minimum": 0, "maximum": 1},
    }
    return build_player_document(
        config=config,
        scene_javascript=SCENE,
        logical_width=760,
        logical_height=620,
        accessible_label="Electric-field vectors and equipotential bands. " + message,
        idle_hint="Press Play to reveal field vectors",
    )
