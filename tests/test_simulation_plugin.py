from __future__ import annotations

from dataclasses import replace

import pytest

from physics_playground.contracts import ContractResult
from physics_playground.models.expansion import REQUIRED_MODE_REQUIREMENTS
from physics_playground.simulation_plugin import (
    CapabilityImplementation,
    PresentationAdapter,
    SimulationPlugin,
    contract_accessible_summary,
    serialize_parameter_set,
)
from physics_playground.simulation_plugin_validation import (
    validate_simulation_plugin,
    validate_simulation_plugins,
)
from physics_playground.subjects.mechanics.cannonball.metadata import SIMULATION
from physics_playground.subjects.mechanics.cannonball.physics import (
    ProjectileParameters,
    ProjectileResult,
    simulate_projectile,
)
from physics_playground.validation import PhysicsValidationError

PAGE = "physics_playground.subjects.mechanics.cannonball.page.render"
RENDERER = "physics_playground.subjects.mechanics.cannonball.scene.build_cannon_canvas"
CAPABILITIES = tuple(
    CapabilityImplementation(capability, PAGE)
    for requirement in REQUIRED_MODE_REQUIREMENTS
    for capability in requirement.capabilities
)


def plugin(**changes: object) -> SimulationPlugin[ProjectileParameters, ProjectileResult]:
    values = {
        "metadata": SIMULATION,
        "parameter_type": ProjectileParameters,
        "result_type": ProjectileResult,
        "model_runner": simulate_projectile,
        "presentation": PresentationAdapter(PAGE, RENDERER),
        "capability_implementations": CAPABILITIES,
        "serialize_notebook_parameters": serialize_parameter_set,
        "accessible_summary": contract_accessible_summary,
        **changes,
    }
    return SimulationPlugin(**values)  # type: ignore[arg-type]


def test_real_contract_derives_identity_and_version_and_validates() -> None:
    candidate = plugin()
    validate_simulation_plugin(candidate)
    assert candidate.id == SIMULATION.id
    assert candidate.model_version == SIMULATION.model_version
    assert candidate.supported_capabilities == {
        capability
        for requirement in REQUIRED_MODE_REQUIREMENTS
        for capability in requirement.capabilities
    }


def test_plugin_catalog_rejects_duplicate_stable_ids() -> None:
    candidate = plugin()
    with pytest.raises(PhysicsValidationError, match="unique"):
        validate_simulation_plugins((candidate, candidate))


@pytest.mark.parametrize("version", ("", "2.0", "projectile-latest", "Projectile-2.0"))
def test_invalid_model_versions_are_rejected(version: str) -> None:
    with pytest.raises(PhysicsValidationError, match="model_version"):
        validate_simulation_plugin(plugin(metadata=replace(SIMULATION, model_version=version)))


def test_runner_annotations_must_match_declared_types() -> None:
    with pytest.raises(PhysicsValidationError, match="return annotation"):
        validate_simulation_plugin(plugin(result_type=ContractResult))


def test_notebook_parameters_must_be_strict_json() -> None:
    with pytest.raises(PhysicsValidationError, match="strict JSON"):
        validate_simulation_plugin(
            plugin(serialize_notebook_parameters=lambda _parameters: {"speed": float("nan")})
        )


def test_each_capability_requires_an_available_implementation() -> None:
    broken = (
        *CAPABILITIES[:-1],
        replace(CAPABILITIES[-1], entrypoint="physics_playground.missing.render"),
    )
    with pytest.raises(PhysicsValidationError, match="capability implementation is unavailable"):
        validate_simulation_plugin(plugin(capability_implementations=broken))


def test_required_capabilities_cannot_be_omitted() -> None:
    with pytest.raises(PhysicsValidationError, match="lack implementations"):
        validate_simulation_plugin(plugin(capability_implementations=CAPABILITIES[:-1]))


def test_accessible_summary_must_be_nonempty_and_stable() -> None:
    with pytest.raises(PhysicsValidationError, match="non-empty"):
        validate_simulation_plugin(plugin(accessible_summary=lambda _result: ""))

    calls = iter(("first", "second"))
    with pytest.raises(PhysicsValidationError, match="stable"):
        validate_simulation_plugin(plugin(accessible_summary=lambda _result: next(calls)))


def test_renderer_must_be_available() -> None:
    with pytest.raises(PhysicsValidationError, match="Renderer is unavailable"):
        validate_simulation_plugin(
            plugin(presentation=PresentationAdapter(PAGE, "physics_playground.missing.render"))
        )
