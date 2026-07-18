"""Unit tests for the pure Bumper Cars collision model."""

import pytest

from physics_playground.subjects.mechanics.bumper_cars.physics import (
    CollisionParameters,
    simulate_collision,
)


def assert_close(actual: float, expected: float, tolerance: float = 1e-10) -> None:
    assert actual == pytest.approx(expected, abs=tolerance, rel=tolerance)


@pytest.mark.parametrize(
    "parameters",
    [
        CollisionParameters(2.0, 3.0, 4.0, 0.0, 1.0),
        CollisionParameters(1.5, 5.0, 6.0, -2.0, 0.4),
        CollisionParameters(4.0, 2.0, -1.0, -3.0, 0.0),
    ],
)
def test_momentum_is_conserved(parameters: CollisionParameters) -> None:
    result = simulate_collision(parameters)
    assert result.collided
    assert_close(
        result.diagnostics.momentum_after_kg_m_s,
        result.diagnostics.momentum_before_kg_m_s,
    )


def test_elastic_collision_conserves_kinetic_energy() -> None:
    result = simulate_collision(CollisionParameters(2.0, 5.0, 7.0, -1.0, 1.0))
    assert_close(
        result.diagnostics.kinetic_energy_after_j,
        result.diagnostics.kinetic_energy_before_j,
    )
    assert_close(result.diagnostics.energy_lost_j, 0.0)


def test_perfectly_inelastic_collision_has_common_final_velocity() -> None:
    parameters = CollisionParameters(2.0, 3.0, 5.0, -1.0, 0.0)
    result = simulate_collision(parameters)
    expected = (2.0 * 5.0 + 3.0 * -1.0) / 5.0
    assert_close(result.velocities_after.car_a_m_s, expected)
    assert_close(result.velocities_after.car_b_m_s, expected)
    assert result.diagnostics.energy_lost_j > 0


def test_equal_masses_exchange_velocities_when_elastic() -> None:
    result = simulate_collision(CollisionParameters(3.0, 3.0, 6.0, -2.0, 1.0))
    assert_close(result.velocities_after.car_a_m_s, -2.0)
    assert_close(result.velocities_after.car_b_m_s, 6.0)


@pytest.mark.parametrize("restitution", [0.0, 0.25, 0.5, 0.8, 1.0])
def test_relative_separation_speed_obeys_restitution(restitution: float) -> None:
    parameters = CollisionParameters(2.0, 4.0, 5.0, -2.0, restitution)
    result = simulate_collision(parameters)
    approach_speed = parameters.velocity_a_m_s - parameters.velocity_b_m_s
    separation_speed = result.velocities_after.car_b_m_s - result.velocities_after.car_a_m_s
    assert_close(separation_speed, restitution * approach_speed)


def test_non_colliding_objects_return_structured_outcome() -> None:
    parameters = CollisionParameters(2.0, 2.0, 1.0, 3.0, 1.0)
    result = simulate_collision(parameters)
    assert not result.collided
    assert not result.completed
    assert result.collision_time_s is None
    assert result.velocities_after == result.velocities_before
    assert result.events[-1].id == "no_collision"
    assert result.warnings


def test_center_of_mass_velocity_matches_total_momentum_over_mass() -> None:
    parameters = CollisionParameters(2.0, 6.0, 8.0, -1.0, 0.5)
    result = simulate_collision(parameters)
    expected = (2.0 * 8.0 + 6.0 * -1.0) / 8.0
    assert_close(result.diagnostics.center_of_mass_velocity_m_s, expected)


def test_collision_result_contains_structured_impact_event() -> None:
    result = simulate_collision(CollisionParameters(2.0, 2.0, 4.0, 0.0, 1.0))
    impact = next(event for event in result.events if event.id == "impact")
    assert impact.kind.value == "collision"
    assert impact.time_s == result.collision_time_s
    assert impact.details["restitution"] == 1.0
