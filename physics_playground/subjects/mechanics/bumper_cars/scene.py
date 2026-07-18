"""Bumper Cars scene adapter for the shared browser-side animation player."""

from physics_playground.canvas.player import build_player_document
from physics_playground.frontend_assets import load_javascript_asset
from physics_playground.serialization import to_jsonable
from physics_playground.subjects.mechanics.bumper_cars.physics import CollisionResult

CANVAS_W, CANVAS_H = 680, 260
PLAYER_HEIGHT = 350

SCENE_JAVASCRIPT = load_javascript_asset("scene-bumper-cars.js")


def build_bumper_canvas(
    result: CollisionResult,
    *,
    final_message: str,
    autoplay: bool,
    nonce: int,
) -> str:
    animation = result.animation
    if animation is None:
        raise ValueError("Bumper Cars result has no animation data.")
    total_time = animation.time_s[-1]
    impact_fraction = (
        result.collision_time_s / total_time
        if result.collision_time_s is not None and total_time > 0
        else 2.0
    )
    config = {
        "durationMs": animation.duration_ms,
        "autoplay": autoplay,
        "seed": 20_260_710 + nonce,
        "trailLength": 14,
        "view": dict(animation.view),
        "tracks": [to_jsonable(track) for track in animation.tracks],
        "impactFraction": impact_fraction,
        "sticky": result.parameters.restitution == 0,
        "completionMessage": final_message,
        "events": (
            [
                {
                    "id": "impact",
                    "fraction": impact_fraction,
                    "type": "particle_burst",
                    "count": 20,
                    "colors": ["#FFD54F", "#FF7043", "#FFEE58", "#FFFFFF"],
                }
            ]
            if result.collided
            else []
        ),
    }
    return build_player_document(
        config=config,
        scene_javascript=SCENE_JAVASCRIPT,
        logical_width=CANVAS_W,
        logical_height=CANVAS_H,
        accessible_label="Two bumper cars moving on a straight track; controls follow the animation.",
        idle_hint="Use Play below or tap CRASH! to launch",
    )


COMPARISON_SCENE_JAVASCRIPT = load_javascript_asset("scene-bumper-cars-comparison.js")


def build_bumper_comparison_canvas(
    baseline: CollisionResult,
    modified: CollisionResult,
    *,
    changed_variable: str,
    nonce: int,
    autoplay: bool,
) -> str:
    """Build a synchronized two-lane player for Run A and Run B."""

    if baseline.animation is None or modified.animation is None:
        raise ValueError("Both comparison results require animation data.")
    minimum = min(baseline.animation.view["minimum"], modified.animation.view["minimum"])
    maximum = max(baseline.animation.view["maximum"], modified.animation.view["maximum"])
    tracks = []
    for prefix, result in (("run_a", baseline), ("run_b", modified)):
        for track in result.animation.tracks:
            payload = to_jsonable(track)
            payload["id"] = f"{prefix}_{track.id}"
            payload["label"] = f"{prefix.replace('_', ' ').title()} {track.label}"
            tracks.append(payload)
    events = []
    for lane, result, offset in (("a", baseline, 0), ("b", modified, 1)):
        total = result.animation.time_s[-1]
        if result.collision_time_s is not None and total > 0:
            fraction = result.collision_time_s / total
            events.append(
                {
                    "id": f"impact_{lane}",
                    "fraction": fraction,
                    "type": "particle_burst",
                    "lane": lane,
                    "trackA": offset * 2,
                    "trackB": offset * 2 + 1,
                    "count": 14,
                    "colors": ["#FFD54F", "#FF7043", "#FFFFFF"],
                }
            )
    config = {
        "durationMs": 4_200,
        "autoplay": autoplay,
        "seed": 20_260_800 + nonce,
        "trailLength": 0,
        "view": {"minimum": minimum, "maximum": maximum},
        "tracks": tracks,
        "events": events,
        "completionMessage": f"Comparison complete: {changed_variable}",
    }
    return build_player_document(
        config=config,
        scene_javascript=COMPARISON_SCENE_JAVASCRIPT,
        logical_width=CANVAS_W,
        logical_height=CANVAS_H,
        accessible_label="Synchronized comparison of Bumper Cars Run A and Run B.",
        idle_hint="Run A is shown above Run B",
    )
