"""Tests for the reusable simulation contract and reference implementation."""

import json

import pytest

from physics_playground.contract_validation import validate_contract_result
from physics_playground.contracts import (
    AnimationData,
    AnimationKind,
    AnimationTrack,
    shared_metric_deltas,
)
from physics_playground.history import TrialHistory
from physics_playground.serialization import dumps
from physics_playground.subjects.mechanics.cannonball.physics import (
    ProjectileParameters,
    simulate_projectile,
)
from physics_playground.validation import PhysicsValidationError


def test_real_simulation_implements_complete_contract() -> None:
    result = simulate_projectile(ProjectileParameters())
    validate_contract_result(result)
    assert result.animation is not None
    assert result.plots
    assert result.metric("impact_speed").value > 0
    assert result.events[-1].id == "impact"
    assert result.assumptions


def test_result_serializes_as_strict_json() -> None:
    result = simulate_projectile(ProjectileParameters())
    payload = json.loads(dumps(result))
    assert payload["simulation_id"] == "cannonball"
    assert payload["parameters"]["launch_speed_m_s"] == 20.0
    assert payload["events"][-1]["kind"] == "completion"
    assert payload["animation"]["kind"] == "two_dimensional"


def test_trial_history_serializes_and_preserves_results() -> None:
    history = TrialHistory[ProjectileParameters]("cannonball")
    trial = history.add(simulate_projectile(ProjectileParameters()), label="First try")
    payload = json.loads(history.to_json())
    assert history.get(trial.id) is trial
    assert payload["trials"][0]["label"] == "First try"


def test_comparison_returns_shared_metric_deltas() -> None:
    slow = simulate_projectile(ProjectileParameters(10.0, 45.0))
    fast = simulate_projectile(ProjectileParameters(20.0, 45.0))
    assert shared_metric_deltas(slow, fast)["range"] > 0


def test_parameter_validation_rejects_nonphysical_height() -> None:
    with pytest.raises(PhysicsValidationError):
        simulate_projectile(ProjectileParameters(launch_speed_m_s=0.0))


def test_animation_validation_rejects_mismatched_lengths() -> None:
    animation = AnimationData(
        kind=AnimationKind.ONE_DIMENSIONAL,
        time_s=(0.0, 1.0),
        tracks=(AnimationTrack("object", "Object", (1.0,)),),
        duration_ms=1_000,
    )
    from physics_playground.contract_validation import validate_animation

    with pytest.raises(PhysicsValidationError):
        validate_animation(animation)
