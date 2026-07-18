"""Shared-asset Earth Tunnel animation adapters."""

from __future__ import annotations

from physics_playground.canvas.player import build_player_document
from physics_playground.frontend_assets import load_javascript_asset
from physics_playground.serialization import to_jsonable

CANVAS_W, CANVAS_H, PLAYER_HEIGHT = 640, 390, 470

SCENE = load_javascript_asset("scene-earth-tunnel.js")


def _acceleration_samples(result) -> list[float]:
    plot = next(item for item in result.plots if item.id == "acceleration_position")
    return list(plot.series[0].y)


def _doc(items, seed, autoplay, message):
    tracks = []
    travelers = []
    roles = ("trajectory", "energy", "selected")
    for i, (label, result, _color) in enumerate(items):
        track = to_jsonable(result.animation.tracks[0])
        track["id"] = f"traveler_{i}"
        track["label"] = label
        track["y"] = _acceleration_samples(result)
        track["style"] = {"role": roles[i % len(roles)]}
        tracks.append(track)
        travelers.append(
            {
                "label": f"{label}: {result.parameters.model.value}",
                "model": result.parameters.model.value,
                "turningPointKm": result.parameters.radius_m
                * result.parameters.start_fraction
                / 1000,
                "role": roles[i % len(roles)],
            }
        )
    radius = max(result.parameters.radius_m / 1000 for _, result, _ in items)
    models = list(dict.fromkeys(result.parameters.model.value for _, result, _ in items))
    config = {
        "durationMs": 4500,
        "autoplay": autoplay,
        "seed": seed,
        "trailLength": 36,
        "frameCount": max(len(track["x"]) for track in tracks),
        "view": {"minimum": -radius, "maximum": radius},
        "radiusKm": radius,
        "earthTunnel": {"travelers": travelers, "modelSummary": " vs. ".join(models)},
        "tracks": tracks,
        "events": [],
        "completionMessage": message,
    }
    return build_player_document(
        config=config,
        scene_javascript=SCENE,
        logical_width=CANVAS_W,
        logical_height=CANVAS_H,
        accessible_label="Travelers on synchronized recorded timelines inside a labeled tunnel, distinguished by labels, solid or dashed trails, and outlines.",
        idle_hint="Use Play or press JUMP IN!",
    )


def build_tunnel_canvas(r, *, seed, autoplay):
    return _doc([("Traveler", r, "")], seed, autoplay, "Reached the opposite turning point")


def build_tunnel_comparison_canvas(items, *, seed, autoplay):
    return _doc(
        [(label, result, color) for label, result, color in items],
        seed,
        autoplay,
        "Comparison complete",
    )
