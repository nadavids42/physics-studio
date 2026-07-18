import pytest

from physics_playground.canvas.player import build_player_document, player_document_cache_info
from physics_playground.notebook import ExperimentNotebook
from physics_playground.performance import (
    MAX_INTEGRATION_STEPS,
    MAX_NOTEBOOK_TRIALS,
    MAX_TRAJECTORY_SAMPLES,
    recommended_time_step,
)
from physics_playground.subjects.mechanics.bumper_cars.physics import CollisionParameters
from physics_playground.subjects.mechanics.cannonball.physics import (
    ProjectileParameters,
    projectile_range_scan,
)
from physics_playground.subjects.mechanics.earth_tunnel.physics import TunnelParameters
from physics_playground.subjects.mechanics.orbital_gravity.physics import OrbitParameters
from physics_playground.subjects.waves_and_oscillations.boing.physics import (
    SpringParameters,
    resonance_sweep,
)
from physics_playground.subjects.waves_and_oscillations.double_pendulum.physics import (
    DoublePendulumParameters,
)
from physics_playground.subjects.waves_and_oscillations.pendulum.physics import PendulumParameters
from physics_playground.validation import PhysicsValidationError


@pytest.mark.parametrize(
    "parameters",
    [
        CollisionParameters(1, 1, float("nan"), 0, 1),
        ProjectileParameters(float("inf"), 45),
        SpringParameters(1, float("nan"), 1),
        PendulumParameters(1, 9.81, float("inf")),
        OrbitParameters(20, 7, float("nan")),
        TunnelParameters(float("inf"), 9.81),
        DoublePendulumParameters(angle_1_deg=float("nan")),
    ],
)
def test_nan_and_infinity_are_rejected(parameters):
    with pytest.raises(PhysicsValidationError):
        parameters.validate()


def test_extreme_computational_budgets_are_rejected():
    with pytest.raises(PhysicsValidationError):
        OrbitParameters(20, 7, 1, steps=MAX_INTEGRATION_STEPS + 1).validate()
    with pytest.raises(PhysicsValidationError):
        ProjectileParameters(20, 45, time_step_s=0.0001, max_time_s=100).validate()
    with pytest.raises(PhysicsValidationError):
        SpringParameters(1, 10, 1, samples=MAX_TRAJECTORY_SAMPLES + 1).validate()


def test_boundary_budget_is_accepted():
    CollisionParameters(1, 1, 1, 0, 1, samples=MAX_TRAJECTORY_SAMPLES).validate()


def test_recommended_time_step_is_deterministic():
    assert recommended_time_step(10, 0.02) == 0.2


def test_parameter_scans_are_cached():
    before = projectile_range_scan.cache_info()
    projectile_range_scan(20, 9.81)
    projectile_range_scan(20, 9.81)
    after = projectile_range_scan.cache_info()
    assert after.hits > before.hits
    before = resonance_sweep.cache_info()
    resonance_sweep(2, 20, 0.3, 4, 5, 7)
    resonance_sweep(2, 20, 0.3, 4, 5, 7)
    assert resonance_sweep.cache_info().hits > before.hits


def test_static_player_html_is_cached_and_seed_is_part_of_payload():
    kwargs = dict(
        scene_javascript="const scene={draw(){}};",
        logical_width=100,
        logical_height=50,
        accessible_label="test",
        idle_hint="play",
    )
    before = player_document_cache_info()
    a = build_player_document(
        config={"durationMs": 1, "seed": 1, "tracks": [], "events": []}, **kwargs
    )
    b = build_player_document(
        config={"durationMs": 1, "seed": 1, "tracks": [], "events": []}, **kwargs
    )
    after = player_document_cache_info()
    assert a == b and after.hits > before.hits


def test_notebook_storage_is_bounded():
    notebook = ExperimentNotebook()
    for index in range(MAX_NOTEBOOK_TRIALS + 3):
        notebook.add_trial(
            simulation_id="test",
            parameters={"x": index},
            prediction=None,
            result_summary="ok",
            metrics={},
            earned_badges=(),
            random_seed=index,
            model_version="test",
        )
    assert len(notebook.trials) == MAX_NOTEBOOK_TRIALS
    assert notebook.trials[0].trial_number == 4
