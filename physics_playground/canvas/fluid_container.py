"""Reusable responsive container renderer for buoyancy and hydrostatic pressure."""

from physics_playground.canvas.player import build_player_document
from physics_playground.frontend_assets import load_javascript_asset

SCENE = load_javascript_asset("scene-fluid-container.js")


def build_fluid_document(
    *,
    kind: str,
    message: str,
    seed: int,
    submerged_fraction: float = 0.0,
    depth: float = 0.0,
    maximum_depth: float = 1.0,
    state: str = "Floating",
    object_density: float = 0.0,
    fluid_density: float = 0.0,
    displaced_volume: float = 0.0,
    weight: float = 0.0,
    buoyant_force: float = 0.0,
    gauge_pressure: float = 0.0,
    absolute_pressure: float = 0.0,
    surface_pressure: float = 0.0,
    pressure_samples: list[dict] | None = None,
) -> str:
    raw_samples = pressure_samples or [
        {"depth": maximum_depth * i / 4, "gauge": gauge_pressure * i / 4} for i in range(5)
    ]
    maximum_gauge = max((float(item["gauge"]) for item in raw_samples), default=1.0) or 1.0
    samples = [
        {
            "depth": float(item["depth"]),
            "ratio": max(0.0, min(1.0, float(item["gauge"]) / maximum_gauge)),
        }
        for item in raw_samples
    ]
    config = {
        "durationMs": 1500,
        "autoplay": False,
        "seed": seed,
        "tracks": [{"id": "fluid-reveal", "label": "Fluid result reveal", "x": [0, 1]}],
        "events": [],
        "completionMessage": message,
        "fluidContainer": {
            "kind": kind,
            "fraction": submerged_fraction,
            "depth": depth,
            "maxDepth": maximum_depth,
            "state": state,
            "objectDensity": object_density,
            "fluidDensity": fluid_density,
            "displacedVolume": displaced_volume,
            "weight": weight,
            "buoyant": buoyant_force,
            "gaugePressure": gauge_pressure,
            "absolutePressure": absolute_pressure,
            "surfacePressure": surface_pressure,
            "pressureSamples": samples,
        },
        "view": {"minimum": 0, "maximum": 1},
    }
    return build_player_document(
        config=config,
        scene_javascript=SCENE,
        logical_width=680,
        logical_height=500,
        accessible_label="Fluid container diagram. " + message,
        idle_hint="Press Play to reveal the fluid result",
    )
