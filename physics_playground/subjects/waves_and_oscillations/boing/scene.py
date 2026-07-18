"""Boing Machine adapters for the shared animation player."""

from __future__ import annotations

from physics_playground.canvas.player import build_player_document
from physics_playground.frontend_assets import load_javascript_asset
from physics_playground.serialization import to_jsonable
from physics_playground.subjects.waves_and_oscillations.boing.physics import SpringResult

CANVAS_W, CANVAS_H, PLAYER_HEIGHT = 680, 300, 360

SCENE = load_javascript_asset("scene-boing.js")


def _velocity_samples(result: SpringResult) -> list[float]:
    velocity_plot = next(plot for plot in result.plots if plot.id == "velocity_time")
    return list(velocity_plot.series[0].y)


def _document(
    results: list[tuple[str, SpringResult, str]], *, seed: int, autoplay: bool, message: str
) -> str:
    minimum = min(r.animation.view["minimum"] for _, r, _ in results)
    maximum = max(r.animation.view["maximum"] for _, r, _ in results)
    tracks = []
    oscillators = []
    roles = ("accent", "energy", "displacement")
    for i, (label, result, _color) in enumerate(results):
        track = to_jsonable(result.animation.tracks[0])
        track["id"] = f"mass_{i}"
        track["label"] = label
        track["y"] = _velocity_samples(result)
        track["style"] = {"role": roles[i % len(roles)]}
        tracks.append(track)
        p = result.parameters
        oscillators.append(
            {
                "initialDisplacementM": p.initial_displacement_m,
                "stiffnessNm": p.stiffness_n_m,
                "dampingNsM": p.damping_n_s_m,
                "massKg": p.mass_kg,
                "durationS": p.duration_s,
                "driven": p.drive_force_n > 0,
                "role": roles[i % len(roles)],
            }
        )
    config = {
        "durationMs": 4200,
        "autoplay": autoplay,
        "seed": seed,
        "trailLength": 12,
        "view": {"minimum": minimum, "maximum": maximum},
        "tracks": tracks,
        "boing": {"oscillators": oscillators},
        "events": [],
        "completionMessage": message,
    }
    return build_player_document(
        config=config,
        scene_javascript=SCENE,
        logical_width=CANVAS_W,
        logical_height=CANVAS_H,
        accessible_label="Masses oscillating horizontally on springs with equilibrium, amplitude, and vector annotations.",
        idle_hint="Use Play or press BOING!",
    )


def build_boing_canvas(result: SpringResult, *, seed: int, autoplay: bool) -> str:
    return _document(
        [("Spring mass", result, "")], seed=seed, autoplay=autoplay, message="Oscillation complete!"
    )


def build_boing_comparison_canvas(
    a: SpringResult, b: SpringResult, *, labels: tuple[str, str], seed: int, autoplay: bool
) -> str:
    return _document(
        [(labels[0], a, ""), (labels[1], b, "")],
        seed=seed,
        autoplay=autoplay,
        message="Comparison complete",
    )
