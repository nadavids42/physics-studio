"""Tests for the reusable simulation contract and reference implementation."""

import json

import pytest

from physics_playground.contract_validation import validate_contract_result
from physics_playground.contracts import AnimationData, AnimationKind, AnimationTrack
from physics_playground.examples import FreeFallParameters, FreeFallSimulation
from physics_playground.history import TrialHistory
from physics_playground.serialization import dumps
from physics_playground.validation import PhysicsValidationError


def test_example_implements_complete_contract() -> None:
    result = FreeFallSimulation().run(FreeFallParameters(height_m=25.0))
    validate_contract_result(result)
    assert result.animation is not None
    assert len(result.plots) == 2
    assert result.metric("impact_speed").value > 0
    assert result.events[-1].id == "impact"
    assert len(result.assumptions) == 2
    assert len(result.missions) == 1


def test_result_serializes_as_strict_json() -> None:
    result = FreeFallSimulation().run(FreeFallParameters())
    payload = json.loads(dumps(result))
    assert payload["simulation_id"] == "free_fall_example"
    assert payload["parameters"]["height_m"] == 20.0
    assert payload["events"][-1]["kind"] == "completion"
    assert payload["animation"]["kind"] == "one_dimensional"


def test_trial_history_serializes_and_preserves_results() -> None:
    simulation = FreeFallSimulation()
    history = TrialHistory[FreeFallParameters](simulation.metadata.id)
    trial = history.add(simulation.run(FreeFallParameters()), label="First try")
    payload = json.loads(history.to_json())
    assert history.get(trial.id) is trial
    assert payload["trials"][0]["label"] == "First try"


def test_comparison_returns_shared_metric_deltas() -> None:
    simulation = FreeFallSimulation()
    short = simulation.run(FreeFallParameters(height_m=5.0))
    tall = simulation.run(FreeFallParameters(height_m=20.0))
    comparison = simulation.compare(short, tall)
    assert comparison.metric_deltas["flight_time"] > 0
    assert comparison.metric_deltas["impact_speed"] > 0


def test_parameter_validation_rejects_nonphysical_height() -> None:
    with pytest.raises(PhysicsValidationError):
        FreeFallSimulation().run(FreeFallParameters(height_m=0.0))


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
