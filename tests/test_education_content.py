"""Validation and sequencing tests for the educational content domain."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from physics_playground.education.catalog import ASSESSMENTS, CURRICULUM, LESSONS_BY_ID
from physics_playground.education.models import (
    ActivityPhase,
    ContentVoice,
    EducationEventKind,
    EducationProgressEvent,
    QuestionKind,
    SimulationActivity,
)
from physics_playground.education.validation import validate_curriculum_manifest
from physics_playground.models.simulations import LearningMode
from physics_playground.registry import SIMULATION_REGISTRY
from physics_playground.subjects.mechanics.cannonball.lesson import (
    CANNONBALL_ASSESSMENTS,
    CANNONBALL_LESSON,
)
from physics_playground.subjects.mechanics.foundations_lesson import MODELS_MEASUREMENTS_LESSON
from physics_playground.subjects.mechanics.kinematics_lessons import KINEMATICS_LESSONS
from physics_playground.validation import PhysicsValidationError

SIMULATION_IDS = {simulation.id for simulation in SIMULATION_REGISTRY}


def _manifest_with_lesson(lesson):
    subject = CURRICULUM.subjects[0]
    source_unit = next(item for item in subject.units if CANNONBALL_LESSON in item.lessons)
    unit = replace(source_unit, lessons=(lesson,))
    return replace(CURRICULUM, subjects=(replace(subject, units=(unit,)),))


def _validate_lesson(lesson) -> None:
    validate_curriculum_manifest(
        _manifest_with_lesson(lesson),
        simulation_ids=SIMULATION_IDS,
        assessments=CANNONBALL_ASSESSMENTS,
    )


def test_builtin_curriculum_is_valid_and_cataloged() -> None:
    validate_curriculum_manifest(CURRICULUM, simulation_ids=SIMULATION_IDS, assessments=ASSESSMENTS)
    assert LESSONS_BY_ID == {
        MODELS_MEASUREMENTS_LESSON.id: MODELS_MEASUREMENTS_LESSON,
        **{lesson.id: lesson for lesson in KINEMATICS_LESSONS},
        CANNONBALL_LESSON.id: CANNONBALL_LESSON,
    }


def test_lesson_domain_has_no_streamlit_or_page_imports() -> None:
    root = Path("physics_playground/education")
    source = "\n".join(path.read_text(encoding="utf-8") for path in root.rglob("*.py"))
    assert "import streamlit" not in source
    assert ".page import" not in source
    assert CANNONBALL_LESSON.simulation_ids == ("cannonball",)


def test_complete_lesson_sequences_every_learning_phase_and_mode() -> None:
    assert tuple(activity.phase for activity in CANNONBALL_LESSON.activity_sequence) == tuple(
        ActivityPhase
    )
    assert tuple(activity.mode for activity in CANNONBALL_LESSON.activity_sequence) == (
        LearningMode.EXPLORE,
        LearningMode.EXPLORE,
        LearningMode.COMPARE,
        LearningMode.ANALYZE,
        LearningMode.MODEL,
        None,
    )


def test_worked_example_contains_reasoning_substitution_units_and_interpretation() -> None:
    examples = [
        component
        for section in CANNONBALL_LESSON.sections
        for component in section.components
        if component.__class__.__name__ == "WorkedExample"
    ]
    assert len(examples) == 1
    example = examples[0]
    assert {known.quantity.symbol for known in example.known_values} == {"v_0", "theta", "g"}
    assert example.unknown.symbol == "R" and example.unknown.unit == "m"
    assert len(example.symbolic_reasoning) == 2
    assert len(example.substitutions) == 2
    assert "dimensions of length" in example.unit_check
    assert "drag" in example.final_interpretation


def test_guided_derivation_supports_progressive_reveal() -> None:
    derivation = CANNONBALL_LESSON.sections[1].components[0]
    assert [step.reveal_order for step in derivation.steps] == [1, 2, 3, 4]
    assert all(step.prompt and step.expression and step.explanation for step in derivation.steps)
    assert derivation.steps[0].hint


def test_content_depth_and_voice_are_independent_from_scientific_structure() -> None:
    advanced_section = CANNONBALL_LESSON.sections[1]
    changed = replace(
        CANNONBALL_LESSON,
        profile=replace(CANNONBALL_LESSON.profile, voice=ContentVoice.CONCISE),
    )
    assert advanced_section.profile.depth.value == "advanced"
    assert advanced_section.profile.voice.value == "academic"
    assert changed.sections == CANNONBALL_LESSON.sections
    assert changed.objectives == CANNONBALL_LESSON.objectives


def test_unknown_simulation_reference_is_rejected() -> None:
    activity = replace(CANNONBALL_LESSON.activity_sequence[0], simulation_id="missing")
    lesson = replace(
        CANNONBALL_LESSON,
        simulation_ids=("missing",),
        activity_sequence=(activity, *CANNONBALL_LESSON.activity_sequence[1:]),
        sections=(
            replace(CANNONBALL_LESSON.sections[0], components=(activity,)),
            *CANNONBALL_LESSON.sections[1:],
        ),
    )
    with pytest.raises(PhysicsValidationError, match="simulation"):
        _validate_lesson(lesson)


def test_out_of_order_activity_phases_are_rejected() -> None:
    sequence = list(CANNONBALL_LESSON.activity_sequence)
    sequence[1], sequence[2] = sequence[2], sequence[1]
    lesson = replace(CANNONBALL_LESSON, activity_sequence=tuple(sequence))
    with pytest.raises(PhysicsValidationError, match="learning sequence"):
        _validate_lesson(lesson)


def test_activity_phase_requires_the_matching_simulation_mode() -> None:
    original = CANNONBALL_LESSON.activity_sequence[3]
    invalid = replace(original, mode=LearningMode.EXPLORE)
    sequence = tuple(
        invalid if item.id == invalid.id else item for item in CANNONBALL_LESSON.activity_sequence
    )
    sections = tuple(
        replace(
            section,
            components=tuple(
                invalid if item.id == invalid.id else item for item in section.components
            ),
        )
        for section in CANNONBALL_LESSON.sections
    )
    with pytest.raises(PhysicsValidationError, match="Analyze"):
        _validate_lesson(replace(CANNONBALL_LESSON, activity_sequence=sequence, sections=sections))


def test_section_activity_sequence_must_match_manifest_sequence() -> None:
    section = CANNONBALL_LESSON.sections[0]
    lesson = replace(
        CANNONBALL_LESSON,
        sections=(replace(section, components=()), *CANNONBALL_LESSON.sections[1:]),
    )
    with pytest.raises(PhysicsValidationError, match="match activity_sequence"):
        _validate_lesson(lesson)


def test_invalid_worked_example_derivation_and_checkpoint_are_rejected() -> None:
    derivation_section = CANNONBALL_LESSON.sections[1]
    derivation = derivation_section.components[0]
    broken_steps = (replace(derivation.steps[0], reveal_order=2), *derivation.steps[1:])
    broken_derivation = replace(derivation, steps=broken_steps)
    lesson = replace(
        CANNONBALL_LESSON,
        sections=(
            CANNONBALL_LESSON.sections[0],
            replace(
                derivation_section,
                components=(broken_derivation, *derivation_section.components[1:]),
            ),
            *CANNONBALL_LESSON.sections[2:],
        ),
    )
    with pytest.raises(PhysicsValidationError, match="reveal_order"):
        _validate_lesson(lesson)

    example_section = CANNONBALL_LESSON.sections[2]
    example = example_section.components[0]
    broken_example = replace(example, known_values=())
    lesson = replace(
        CANNONBALL_LESSON,
        sections=(
            *CANNONBALL_LESSON.sections[:2],
            replace(example_section, components=(broken_example, *example_section.components[1:])),
            CANNONBALL_LESSON.sections[3],
        ),
    )
    with pytest.raises(PhysicsValidationError, match="known values"):
        _validate_lesson(lesson)

    checkpoint = example_section.components[1]
    assert checkpoint.kind is QuestionKind.MULTIPLE_CHOICE
    broken_checkpoint = replace(checkpoint, objective_ids=("missing",))
    lesson = replace(
        CANNONBALL_LESSON,
        sections=(
            *CANNONBALL_LESSON.sections[:2],
            replace(
                example_section,
                components=(example, broken_checkpoint, *example_section.components[2:]),
            ),
            CANNONBALL_LESSON.sections[3],
        ),
    )
    with pytest.raises(PhysicsValidationError, match="objectives"):
        _validate_lesson(lesson)


def test_duplicate_ids_and_invalid_unit_objectives_are_rejected() -> None:
    duplicate = replace(
        CANNONBALL_LESSON,
        objectives=(CANNONBALL_LESSON.objectives[0], CANNONBALL_LESSON.objectives[0]),
    )
    with pytest.raises(PhysicsValidationError, match="unique"):
        _validate_lesson(duplicate)
    subject = CURRICULUM.subjects[0]
    bad_unit = replace(subject.units[0], objective_ids=("missing",))
    manifest = replace(CURRICULUM, subjects=(replace(subject, units=(bad_unit,)),))
    with pytest.raises(PhysicsValidationError, match="Unit expectations"):
        validate_curriculum_manifest(
            manifest, simulation_ids=SIMULATION_IDS, assessments=CANNONBALL_ASSESSMENTS
        )


def test_progress_event_is_typed_without_presentation_state() -> None:
    event = EducationProgressEvent(
        "event-1",
        EducationEventKind.ACTIVITY_COMPLETED,
        "learner-1",
        CANNONBALL_LESSON.id,
        datetime(2026, 7, 18, tzinfo=UTC),
        activity_id="predict-angle",
        completed=True,
        score=1.0,
    )
    assert event.kind is EducationEventKind.ACTIVITY_COMPLETED
    assert event.completed and event.score == 1.0


def test_activity_contract_accepts_renderer_independent_presets() -> None:
    activity = SimulationActivity(
        "activity",
        ActivityPhase.EXPLORATION,
        "cannonball",
        "Explore",
        ("Run the model.",),
        LearningMode.EXPLORE,
        {"initial_speed_m_s": 12.0, "drag_enabled": False},
    )
    assert activity.parameter_preset["initial_speed_m_s"] == 12.0
