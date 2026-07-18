"""Cannonball scene adapters for the shared animation player."""

from physics_playground.canvas.player import build_player_document
from physics_playground.frontend_assets import load_javascript_asset
from physics_playground.serialization import to_jsonable
from physics_playground.subjects.mechanics.cannonball.physics import ProjectileResult

CANVAS_W, CANVAS_H, PLAYER_HEIGHT = 680, 360, 440

SCENE = load_javascript_asset("scene-cannonball.js")


def _config(
    results: list[tuple[str, ProjectileResult, str]],
    target_m: float,
    seed: int,
    message: str,
    autoplay: bool,
) -> dict:
    tracks = []
    events = []
    x_max = max(target_m, *(result.range_m for _, result, _ in results)) * 1.15 + 3
    y_max = max(1.0, *(result.maximum_height_m for _, result, _ in results)) * 1.25 + 1
    for index, (label, result, color) in enumerate(results):
        track = to_jsonable(result.animation.tracks[0])
        track["id"] = f"projectile_{index}"
        track["label"] = label
        track["style"] = {"color": color}
        tracks.append(track)
        if result.landed:
            events.append(
                {
                    "id": f"impact_{index}",
                    "fraction": 1.0,
                    "type": "impact",
                    "track": index,
                    "count": 24,
                    "colors": ["#FFD54F", color, "#FFFFFF"],
                }
            )
    return {
        "durationMs": 3_200,
        "autoplay": autoplay,
        "seed": seed,
        "trailLength": 22,
        "view": {"xMin": 0.0, "xMax": x_max, "yMin": 0.0, "yMax": y_max},
        "tracks": tracks,
        "events": events,
        "target": target_m,
        "angle": results[0][1].parameters.launch_angle_deg,
        "completionMessage": message,
    }


def build_cannon_canvas(
    result: ProjectileResult, *, target_m: float, message: str, seed: int, autoplay: bool
) -> str:
    return build_player_document(
        config=_config([("Cannonball", result, "#37474F")], target_m, seed, message, autoplay),
        scene_javascript=SCENE,
        logical_width=CANVAS_W,
        logical_height=CANVAS_H,
        accessible_label="Animated cannonball trajectory and target.",
        idle_hint="Use Play or press FIRE!",
    )


def build_cannon_comparison_canvas(
    run_a: ProjectileResult,
    run_b: ProjectileResult,
    *,
    target_m: float,
    labels: tuple[str, str],
    seed: int,
    autoplay: bool,
) -> str:
    config = _config(
        [(labels[0], run_a, "#1565C0"), (labels[1], run_b, "#E65100")],
        target_m,
        seed,
        "Comparison complete",
        autoplay,
    )
    return build_player_document(
        config=config,
        scene_javascript=SCENE,
        logical_width=CANVAS_W,
        logical_height=CANVAS_H,
        accessible_label=f"Overlaid cannonball trajectories comparing {labels[0]} and {labels[1]}.",
        idle_hint="Run A is blue; Run B is orange",
    )
