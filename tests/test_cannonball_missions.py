from physics_playground.missions.cannonball import evaluate_cannonball_missions
from physics_playground.models.projectile import ProjectileParameters, simulate_no_drag


def completed(result, target):
    return {
        item.mission_id for item in evaluate_cannonball_missions(result, target) if item.completed
    }


def test_existing_cannonball_badges_are_preserved() -> None:
    result = simulate_no_drag(ProjectileParameters(20, 45, 1.62))
    ids = completed(result, result.range_m)
    assert {"cannon_sweet_spot", "cannon_bullseye", "cannon_moon"} <= ids
