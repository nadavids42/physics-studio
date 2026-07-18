import math

import pytest

from physics_playground.subjects.fluids_and_matter.diffusion.physics import (
    MAX_PARTICLES,
    MAX_STEPS,
    MAX_UPDATES,
    DiffusionParameters,
    WalkDimension,
    simulate,
)
from physics_playground.validation import PhysicsValidationError


def test_seeded_runs_are_exactly_reproducible() -> None:
    parameters = DiffusionParameters(particle_count=200, steps=80, seed=42)
    assert simulate(parameters) == simulate(parameters)


def test_unbiased_one_dimensional_mean_is_near_zero() -> None:
    result = simulate(
        DiffusionParameters(
            particle_count=4000,
            dimensions=WalkDimension.ONE_D,
            steps=200,
            step_size_m=0.1,
            seed=1234,
        )
    )
    assert abs(result.mean_displacement_x_m) < 0.08
    assert result.mean_displacement_y_m == 0


def test_unbiased_msd_matches_random_walk_expectation() -> None:
    parameters = DiffusionParameters(
        particle_count=4000, dimensions=WalkDimension.TWO_D, steps=200, step_size_m=0.1, seed=5678
    )
    result = simulate(parameters)
    expected = parameters.steps * parameters.step_size_m**2
    assert result.mean_squared_displacement_m2 == pytest.approx(expected, rel=0.08)


def test_bias_moves_the_ensemble_mean_by_expected_amount() -> None:
    parameters = DiffusionParameters(
        particle_count=3000,
        dimensions=WalkDimension.TWO_D,
        steps=150,
        step_size_m=0.1,
        bias_x=0.3,
        bias_y=-0.2,
        seed=91,
    )
    result = simulate(parameters)
    assert result.mean_displacement_x_m == pytest.approx(
        parameters.steps * parameters.step_size_m * parameters.bias_x, abs=0.08
    )
    assert result.mean_displacement_y_m == pytest.approx(
        parameters.steps * parameters.step_size_m * parameters.bias_y, abs=0.08
    )


def test_step_size_and_timestep_set_diffusion_coefficient() -> None:
    parameters = DiffusionParameters(
        dimensions=WalkDimension.TWO_D, step_size_m=0.2, timestep_s=0.5
    )
    result = simulate(parameters)
    assert result.diffusion_coefficient_m2_s == pytest.approx(0.2**2 / (4 * 0.5))
    assert result.elapsed_time_s == pytest.approx(parameters.steps * 0.5)


def test_visual_output_is_bounded_for_large_runs() -> None:
    result = simulate(DiffusionParameters(particle_count=5000, steps=200))
    assert result.sampled_particle_count == 300
    assert len(result.final_x_m) == 300
    assert len(result.sample_trajectories) == 12
    assert all(len(path) <= 202 for path in result.sample_trajectories)


@pytest.mark.parametrize(
    "changes",
    [
        {"particle_count": 0},
        {"particle_count": MAX_PARTICLES + 1},
        {"steps": 0},
        {"steps": MAX_STEPS + 1},
        {"step_size_m": 0},
        {"timestep_s": 0},
        {"bias_x": 1.1},
        {"bias_y": -1.1},
        {"bias_x": 0.8, "bias_y": 0.8},
        {"step_size_m": math.inf},
        {"seed": True},
        {"dimensions": WalkDimension.ONE_D, "bias_y": 0.1},
    ],
)
def test_invalid_boundary_and_extreme_parameters(changes) -> None:
    values = {
        name: getattr(DiffusionParameters(), name)
        for name in DiffusionParameters.__dataclass_fields__
    }
    values.update(changes)
    with pytest.raises(PhysicsValidationError):
        simulate(DiffusionParameters(**values))


def test_computational_budget_is_enforced() -> None:
    with pytest.raises(PhysicsValidationError, match="too much work"):
        simulate(DiffusionParameters(particle_count=1000, steps=MAX_UPDATES // 1000 + 1))
