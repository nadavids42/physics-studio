"""Consistency checks for reusable simulation bindings and setup presets."""

from dataclasses import replace
import json

import pytest

from physics_playground.model_metadata import MODEL_METADATA, PROJECTILE_MODEL_METADATA
from physics_playground.models.simulations import InteractiveMode, SimulationMode
from physics_playground.presentation.learning_modes import LearningMode
from physics_playground.registry import LEARNING_MODES, SIMULATIONS_BY_ID
from physics_playground.serialization import dumps
from physics_playground.setup_handoff import (
    SETUP_REQUEST_KEY,
    consume_setup_request,
    queue_preset,
)
from physics_playground.simulation_binding import ExpectedMetric, SimulationPreset
from physics_playground.simulation_bindings import (
    PROJECTILE_BINDING,
    PROJECTILE_WORKED_EXAMPLE_PRESET,
    binding_for,
    preset_for,
)
from physics_playground.validation import PhysicsValidationError


def test_interactive_mode_is_canonical_with_legacy_compatibility() -> None:
    assert LearningMode is InteractiveMode
    assert LEARNING_MODES == tuple(InteractiveMode)
    assert InteractiveMode.EXPLORE == SimulationMode.EXPLORE


def test_every_registered_simulation_has_authoritative_metadata() -> None:
    assert set(MODEL_METADATA) == set(SIMULATIONS_BY_ID)


def test_projectile_binding_runs_a_versioned_contract_result() -> None:
    result = PROJECTILE_BINDING.run(PROJECTILE_WORKED_EXAMPLE_PRESET.parameters)
    assert result.simulation_id == "cannonball"
    assert result.model_version == SIMULATIONS_BY_ID["cannonball"].model_version
    assert result.assumptions == PROJECTILE_MODEL_METADATA.assumptions
    assert PROJECTILE_BINDING.metric(result, "range").unit == "m"


def test_projectile_preset_round_trips_and_matches_expected_metrics() -> None:
    payload = json.loads(dumps(PROJECTILE_WORKED_EXAMPLE_PRESET))
    restored = SimulationPreset.from_dict(payload)
    assert restored == PROJECTILE_WORKED_EXAMPLE_PRESET
    result = PROJECTILE_BINDING.run_preset(restored)
    assert result.range_m == pytest.approx(38.31570319208596)


def test_binding_and_preset_catalog_lookups_are_stable() -> None:
    assert binding_for("cannonball") is PROJECTILE_BINDING
    assert preset_for(PROJECTILE_WORKED_EXAMPLE_PRESET.id) is PROJECTILE_WORKED_EXAMPLE_PRESET


def test_preset_rejects_wrong_model_version_and_bad_expectation() -> None:
    wrong_version = replace(PROJECTILE_WORKED_EXAMPLE_PRESET, model_version="projectile-old")
    with pytest.raises(PhysicsValidationError, match="versions"):
        PROJECTILE_BINDING.run_preset(wrong_version)

    bad_expectation = replace(
        PROJECTILE_WORKED_EXAMPLE_PRESET,
        expected_metrics=(ExpectedMetric("range", 1.0),),
    )
    with pytest.raises(PhysicsValidationError, match="expected"):
        PROJECTILE_BINDING.run_preset(bad_expectation)


def test_preset_uses_the_same_setup_handoff_as_notebook_reuse() -> None:
    state = {}
    queue_preset(state, PROJECTILE_WORKED_EXAMPLE_PRESET)
    assert SETUP_REQUEST_KEY in state
    assert consume_setup_request(state, "pendulum") is None
    request = consume_setup_request(state, "cannonball")
    assert request is not None
    assert request.preset_id == PROJECTILE_WORKED_EXAMPLE_PRESET.id
    assert request.parameters == PROJECTILE_WORKED_EXAMPLE_PRESET.parameters
    assert SETUP_REQUEST_KEY not in state

