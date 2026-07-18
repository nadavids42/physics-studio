"""Validation gates used before an expansion simulation enters the registry."""

from physics_playground.models.expansion import (
    REQUIRED_MODE_REQUIREMENTS,
    ExpansionDefinition,
    PresentationCapability,
)
from physics_playground.validation import PhysicsValidationError


def validate_expansion_definition(definition: ExpansionDefinition) -> None:
    metadata = definition.metadata
    if not all((metadata.id, metadata.title, metadata.model_version, metadata.central_question)):
        raise PhysicsValidationError("Expansion metadata is incomplete.")
    required_modes = {item.mode for item in REQUIRED_MODE_REQUIREMENTS}
    declared_modes = {item.mode for item in definition.mode_requirements}
    if declared_modes != required_modes or not required_modes.issubset(metadata.modes):
        raise PhysicsValidationError(
            "Every expansion simulation must implement exactly the four learning modes."
        )
    required_by_mode = {item.mode: set(item.capabilities) for item in REQUIRED_MODE_REQUIREMENTS}
    for mode in definition.mode_requirements:
        if not required_by_mode[mode.mode].issubset(mode.capabilities):
            raise PhysicsValidationError(f"{mode.mode.value} is missing required capabilities.")
    if (
        not definition.parameter_model
        or not definition.result_model
        or not definition.physics_entrypoint
    ):
        raise PhysicsValidationError("Typed model and physics entrypoints are required.")
    if not definition.page_entrypoint:
        raise PhysicsValidationError("A Streamlit page entrypoint is required.")
    if len(definition.missions) < 3:
        raise PhysicsValidationError("Every expansion simulation requires at least three missions.")
    if any(mission.simulation_id != metadata.id for mission in definition.missions):
        raise PhysicsValidationError("Mission simulation IDs must match expansion metadata.")
    if not definition.assumptions or not definition.limitations:
        raise PhysicsValidationError("Model assumptions and limitations are required.")
    if definition.tests.analytic_or_invariant_tests < 2 or definition.tests.validation_tests < 3:
        raise PhysicsValidationError(
            "Expansion simulations need physics invariants and boundary validation tests."
        )
    if PresentationCapability.PREDICTION not in next(
        item.capabilities for item in definition.mode_requirements if item.mode.value == "Explore"
    ):
        raise PhysicsValidationError(
            "Explore mode must collect a prediction before revealing results."
        )
