"""Physics tests for analytic and quadratic-drag projectile models."""

import math

import pytest

from physics_playground.models.projectile import (
    ProjectileParameters,
    simulate_no_drag,
    simulate_quadratic_drag,
)


@pytest.mark.parametrize(
    "speed,angle,gravity", [(20.0, 30.0, 9.81), (35.0, 45.0, 9.81), (18.0, 60.0, 1.62)]
)
def test_no_drag_matches_analytic_formulas(speed: float, angle: float, gravity: float) -> None:
    result = simulate_no_drag(ProjectileParameters(speed, angle, gravity))
    theta = math.radians(angle)
    expected_range = speed**2 * math.sin(2 * theta) / gravity
    expected_height = (speed * math.sin(theta)) ** 2 / (2 * gravity)
    expected_time = 2 * speed * math.sin(theta) / gravity
    assert result.range_m == pytest.approx(expected_range, rel=1e-12)
    assert result.maximum_height_m == pytest.approx(expected_height, rel=2e-4)
    assert result.flight_time_s == pytest.approx(expected_time, rel=1e-12)


def test_maximum_level_ground_range_is_approximately_45_degrees() -> None:
    results = {
        angle: simulate_no_drag(ProjectileParameters(25.0, angle, 9.81)).range_m
        for angle in range(5, 90)
    }
    assert max(results, key=results.get) == 45


def test_complementary_angles_have_equal_no_drag_range() -> None:
    low = simulate_no_drag(ProjectileParameters(25, 30, 9.81))
    high = simulate_no_drag(ProjectileParameters(25, 60, 9.81))
    assert low.range_m == pytest.approx(high.range_m, rel=1e-12)


def test_drag_ground_impact_is_interpolated_to_exact_zero() -> None:
    result = simulate_quadratic_drag(
        ProjectileParameters(30, 40, 9.81, drag_coefficient_kg_m=0.08, time_step_s=0.02)
    )
    assert result.landed
    assert result.animation.tracks[0].y[-1] == 0.0
    assert result.events[-1].id == "impact"


def test_drag_reduces_range_and_mechanical_energy() -> None:
    no_drag = simulate_no_drag(ProjectileParameters(30, 40, 9.81))
    drag = simulate_quadratic_drag(ProjectileParameters(30, 40, 9.81, drag_coefficient_kg_m=0.08))
    assert drag.range_m < no_drag.range_m
    assert drag.metric("energy_lost").value > 0


def test_non_landing_limit_returns_clear_failure() -> None:
    result = simulate_quadratic_drag(
        ProjectileParameters(30, 80, 1.62, drag_coefficient_kg_m=0.01, max_time_s=0.1)
    )
    assert not result.landed
    assert not result.completed
    assert result.events[-1].id == "not_landed"
    assert result.warnings
