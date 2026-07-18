"""Launch-gated Cannonball badge rules."""

from physics_playground.contracts import MissionEvaluation
from physics_playground.models.projectile import ProjectileResult
from physics_playground.units import MOON_GRAVITY_M_S2


def evaluate_cannonball_missions(
    result: ProjectileResult, target_m: float
) -> tuple[MissionEvaluation, ...]:
    if not result.landed:
        return ()
    p = result.parameters
    return (
        MissionEvaluation(
            "cannon_sweet_spot",
            43 <= p.launch_angle_deg <= 47,
            "Launch close to the 45° no-drag sweet spot.",
        ),
        MissionEvaluation(
            "cannon_bullseye",
            abs(result.range_m - target_m) <= 2.0,
            "Land within 2 meters of the target.",
            {"miss_distance_m": abs(result.range_m - target_m)},
        ),
        MissionEvaluation(
            "cannon_moon",
            abs(p.gravity_m_s2 - MOON_GRAVITY_M_S2) < 0.01,
            "Launch a cannonball on the Moon.",
        ),
    )
