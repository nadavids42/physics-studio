"""Reusable responsive shared-player renderer for geometric ray diagrams."""

from physics_playground.canvas.player import build_player_document
from physics_playground.frontend_assets import load_javascript_asset

SCENE = load_javascript_asset("scene-ray-diagram.js")


def build_ray_diagram(
    *,
    rays: list[dict],
    message: str,
    seed: int,
    interface: bool = False,
    lens: bool = False,
    lens_sign: int = 1,
    bounds: tuple[float, float, float, float] = (-5, 5, -4, 4),
    medium_1: float = 1.0,
    medium_2: float = 1.5,
    incident_angle_deg: float = 0.0,
    refraction_angle_deg: float | None = None,
    total_internal_reflection: bool = False,
) -> str:
    xmin, xmax, ymin, ymax = bounds
    config = {
        "durationMs": 1800,
        "autoplay": False,
        "seed": seed,
        "tracks": [{"id": "ray-progress", "label": "Ray construction", "x": [0, 1]}],
        "events": [],
        "completionMessage": message,
        "rayConfig": {
            "rays": rays,
            "interface": interface,
            "lens": lens,
            "lensSign": lens_sign,
            "xmin": xmin,
            "xmax": xmax,
            "ymin": ymin,
            "ymax": ymax,
            "medium1": medium_1,
            "medium2": medium_2,
            "incidentAngle": incident_angle_deg,
            "refractionAngle": refraction_angle_deg,
            "totalInternalReflection": total_internal_reflection,
        },
        "view": {"minimum": 0, "maximum": 1},
    }
    return build_player_document(
        config=config,
        scene_javascript=SCENE,
        logical_width=820,
        logical_height=430,
        accessible_label="Geometric ray diagram. " + message,
        idle_hint="Press Play to construct the rays",
    )
