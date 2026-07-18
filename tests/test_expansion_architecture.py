from dataclasses import replace

import pytest

from physics_playground.contracts import ModelAssumption
from physics_playground.expansion_validation import validate_expansion_definition
from physics_playground.missions.definitions import MissionDefinition, MissionType
from physics_playground.models.expansion import (
    REQUIRED_MODE_REQUIREMENTS,
    ExpansionDefinition,
    SubjectArea,
    TestRequirements,
)
from physics_playground.models.simulations import Difficulty, SimulationDefinition
from physics_playground.validation import PhysicsValidationError


def mission(number: int) -> MissionDefinition:
    return MissionDefinition(
        f"sample_{number}",
        "sample",
        f"Mission {number}",
        "Try it",
        ("Hint",),
        MissionType.DISCOVERY,
        Difficulty.BEGINNER,
        (),
        False,
        f"run:sample_{number}",
        "Sample",
    )


def valid_definition() -> ExpansionDefinition:
    metadata = SimulationDefinition(
        "sample",
        "Sample",
        "🧪",
        "Description",
        "physics_playground.pages.sample",
        "Sample",
        tuple(item.mode for item in REQUIRED_MODE_REQUIREMENTS),
        "What changes?",
        ("Testing",),
        Difficulty.BEGINNER,
        3,
        "shared-browser-player",
        "sample-1.0",
    )
    return ExpansionDefinition(
        metadata,
        SubjectArea.MECHANICS,
        "SampleParameters",
        "SampleResult",
        "physics_playground.subjects.mechanics.sample.physics.simulate",
        "physics_playground.subjects.mechanics.sample.page.render",
        "physics_playground.subjects.mechanics.sample.canvas.build",
        REQUIRED_MODE_REQUIREMENTS,
        tuple(mission(i) for i in range(3)),
        (ModelAssumption("ideal", "Ideal model"),),
        ("Ignores losses",),
    )


def test_complete_expansion_definition_passes() -> None:
    validate_expansion_definition(valid_definition())


def test_all_four_subject_areas_are_stable() -> None:
    assert {item.value for item in SubjectArea} == {
        "mechanics",
        "waves_and_oscillations",
        "light_and_electricity",
        "fluids_and_matter",
    }


def test_missing_missions_is_rejected() -> None:
    definition = valid_definition()
    with pytest.raises(PhysicsValidationError):
        validate_expansion_definition(replace(definition, missions=definition.missions[:2]))


def test_insufficient_boundary_tests_are_rejected() -> None:
    definition = valid_definition()
    with pytest.raises(PhysicsValidationError):
        validate_expansion_definition(
            replace(definition, tests=TestRequirements(validation_tests=2))
        )


def test_mission_ids_must_match_simulation() -> None:
    definition = valid_definition()
    bad = replace(definition.missions[0], simulation_id="another")
    with pytest.raises(PhysicsValidationError):
        validate_expansion_definition(replace(definition, missions=(bad, *definition.missions[1:])))
