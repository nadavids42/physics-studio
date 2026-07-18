"""Mission rules are evaluated from launched results, independently of Streamlit."""

from physics_playground.subjects.mechanics.bumper_cars.missions import evaluate_bumper_missions
from physics_playground.subjects.mechanics.bumper_cars.physics import (
    CollisionParameters,
    simulate_collision,
)


def completed_ids(parameters: CollisionParameters) -> set[str]:
    result = simulate_collision(parameters)
    return {
        evaluation.mission_id
        for evaluation in evaluate_bumper_missions(result)
        if evaluation.completed
    }


def test_equal_mass_swap_badge() -> None:
    assert "collision_swap" in completed_ids(CollisionParameters(2.0, 2.0, 4.0, 0.0, 1.0))


def test_balanced_sticky_collision_stop_badge() -> None:
    assert "collision_stop" in completed_ids(CollisionParameters(2.0, 2.0, 4.0, -4.0, 0.0))


def test_light_car_bounces_from_heavy_car_badge() -> None:
    assert "collision_bounce" in completed_ids(CollisionParameters(1.0, 3.0, 4.0, 0.0, 1.0))


def test_non_collision_cannot_complete_observational_badges() -> None:
    result = simulate_collision(CollisionParameters(2.0, 2.0, 1.0, 3.0, 1.0))
    assert evaluate_bumper_missions(result) == ()
