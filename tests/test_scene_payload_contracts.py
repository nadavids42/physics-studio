"""Representative contracts at the validated Python-to-scene boundary."""

from __future__ import annotations

import json
import re

from physics_playground.canvas.player import build_player_document
from physics_playground.canvas.ray_diagram import SCENE as RAY_SCENE
from physics_playground.subjects.mechanics.cannonball.scene import SCENE as CANNON_SCENE
from physics_playground.subjects.waves_and_oscillations.pendulum.scene import (
    SCENE as PENDULUM_SCENE,
)


def _serialized_payload(document: str) -> dict:
    match = re.search(r"const playerConfig=(\{.*?\});\n", document)
    assert match
    return json.loads(match.group(1))


def _document(scene: str, config: dict) -> str:
    return build_player_document(
        config=config,
        scene_javascript=scene,
        logical_width=640,
        logical_height=360,
        accessible_label="Payload contract",
        idle_hint="Play",
    )


def test_mechanics_payload_preserves_recorded_trajectory_and_units() -> None:
    tracks = [{"id": "projectile", "label": "Ball", "x": [0.0, 2.5], "y": [0.0, 1.2]}]
    payload = _serialized_payload(
        _document(
            CANNON_SCENE,
            {
                "durationMs": 1200,
                "tracks": tracks,
                "events": [],
                "angle": 45.0,
                "target": 8.0,
                "view": {"xMin": 0.0, "xMax": 10.0, "yMin": 0.0, "yMax": 5.0},
            },
        )
    )
    assert payload["tracks"] == tracks
    assert payload["angle"] == 45.0
    assert payload["target"] == 8.0


def test_oscillation_payload_preserves_cartesian_tracks_and_scale() -> None:
    tracks = [{"id": "bob", "x": [0.0, 0.4], "y": [-2.0, -1.9]}]
    payload = _serialized_payload(
        _document(
            PENDULUM_SCENE,
            {"durationMs": 1000, "tracks": tracks, "events": [], "maxLength": 2.0},
        )
    )
    assert payload["tracks"] == tracks
    assert payload["maxLength"] == 2.0


def test_optics_payload_preserves_ray_geometry_and_medium_parameters() -> None:
    ray_config = {
        "rays": [{"x1": -2.0, "y1": 1.0, "x2": 2.0, "y2": -1.0}],
        "interface": True,
        "medium1": 1.0,
        "medium2": 1.5,
        "incidentAngle": 30.0,
        "refractionAngle": 19.47,
    }
    payload = _serialized_payload(
        _document(
            RAY_SCENE,
            {
                "durationMs": 1000,
                "tracks": [{"id": "ray-progress", "x": [0, 1]}],
                "events": [],
                "rayConfig": ray_config,
            },
        )
    )
    assert payload["rayConfig"] == ray_config
