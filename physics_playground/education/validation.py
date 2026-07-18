"""Validation gates for curriculum manifests and lesson sequencing."""

from __future__ import annotations

import math
from collections.abc import Iterable

from physics_playground.education.models import (
    ActivityPhase,
    CheckpointQuestion,
    CurriculumManifest,
    GuidedDerivation,
    Lesson,
    PrerequisiteKind,
    QuestionKind,
    SimulationActivity,
    WorkedExample,
)
from physics_playground.models.simulations import InteractiveMode
from physics_playground.validation import PhysicsValidationError

PHASE_ORDER = tuple(ActivityPhase)
EXPECTED_MODES = {
    ActivityPhase.PREDICTION: InteractiveMode.EXPLORE,
    ActivityPhase.EXPLORATION: InteractiveMode.EXPLORE,
    ActivityPhase.COMPARISON: InteractiveMode.COMPARE,
    ActivityPhase.ANALYSIS: InteractiveMode.ANALYZE,
    ActivityPhase.MODELING: InteractiveMode.MODEL,
}


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise PhysicsValidationError(f"{label} cannot be blank.")


def _unique_ids(items: Iterable[object], label: str) -> set[str]:
    ids = []
    for item in items:
        item_id = getattr(item, "id", "")
        _require_text(item_id, f"{label} ID")
        ids.append(item_id)
    if len(ids) != len(set(ids)):
        raise PhysicsValidationError(f"{label} IDs must be unique.")
    return set(ids)


def _validate_worked_example(example: WorkedExample) -> None:
    if not example.known_values:
        raise PhysicsValidationError("Worked examples require known values.")
    if not example.unknown.symbol or not example.unknown.unit:
        raise PhysicsValidationError("Worked examples require an unknown quantity and unit.")
    if not example.symbolic_reasoning or not example.substitutions:
        raise PhysicsValidationError(
            "Worked examples require symbolic reasoning and substitutions."
        )
    for known in example.known_values:
        if not math.isfinite(known.value) or not known.quantity.unit:
            raise PhysicsValidationError("Known values must be finite and include units.")
    for label, value in (
        ("unit check", example.unit_check),
        ("final answer", example.final_answer),
        ("final interpretation", example.final_interpretation),
    ):
        _require_text(value, f"Worked-example {label}")


def _validate_derivation(derivation: GuidedDerivation) -> None:
    if not derivation.assumptions or not derivation.steps:
        raise PhysicsValidationError("Guided derivations require assumptions and reveal steps.")
    orders = [step.reveal_order for step in derivation.steps]
    if orders != list(range(1, len(orders) + 1)):
        raise PhysicsValidationError("Derivation reveal_order must be consecutive starting at one.")
    _unique_ids(derivation.steps, "Derivation step")


def _validate_checkpoint(question: CheckpointQuestion, objective_ids: set[str]) -> None:
    if not question.objective_ids or not set(question.objective_ids) <= objective_ids:
        raise PhysicsValidationError("Checkpoint objectives must reference lesson objectives.")
    if question.kind is QuestionKind.MULTIPLE_CHOICE:
        choice_ids = _unique_ids(question.choices, "Answer choice")
        if len(choice_ids) < 2 or question.correct_answer not in choice_ids:
            raise PhysicsValidationError("Multiple-choice checkpoints need a valid correct choice.")
    elif not question.correct_answer:
        raise PhysicsValidationError("Numeric and short-response checkpoints need an answer.")
    if question.kind is QuestionKind.NUMERIC and (
        question.tolerance is None or question.tolerance < 0
    ):
        raise PhysicsValidationError("Numeric checkpoints require a nonnegative tolerance.")


def _validate_activity(
    activity: SimulationActivity, lesson: Lesson, simulation_ids: set[str]
) -> None:
    if activity.simulation_id not in simulation_ids:
        raise PhysicsValidationError(f"Unknown simulation reference: {activity.simulation_id}.")
    if activity.simulation_id not in lesson.simulation_ids:
        raise PhysicsValidationError(
            "Activities must reference a simulation declared by the lesson."
        )
    if not activity.instructions or not all(item.strip() for item in activity.instructions):
        raise PhysicsValidationError("Simulation activities require actionable instructions.")
    expected = EXPECTED_MODES.get(activity.phase)
    if expected is not None and activity.mode is not expected:
        raise PhysicsValidationError(
            f"{activity.phase.value} activities must use {expected.value} mode."
        )


def _validate_lesson(lesson: Lesson, concept_ids: set[str], simulation_ids: set[str]) -> None:
    _require_text(lesson.title, "Lesson title")
    _require_text(lesson.summary, "Lesson summary")
    _require_text(lesson.next_lesson_title, "Next lesson title")
    if lesson.estimated_minutes <= 0:
        raise PhysicsValidationError("Lesson duration must be positive.")
    objective_ids = _unique_ids(lesson.objectives, "Learning objective")
    if not objective_ids or not lesson.sections:
        raise PhysicsValidationError("Lessons require objectives and sections.")
    if not set(lesson.concept_ids) <= concept_ids:
        raise PhysicsValidationError("Lesson concept references must exist in its subject.")
    if len(lesson.simulation_ids) != len(set(lesson.simulation_ids)):
        raise PhysicsValidationError("Lesson simulation references must be unique.")
    if not lesson.simulation_ids or not set(lesson.simulation_ids) <= simulation_ids:
        raise PhysicsValidationError("Lesson simulation references must exist in the registry.")
    for objective in lesson.objectives:
        _require_text(objective.statement, "Learning objective statement")
        _require_text(objective.evidence, "Learning objective evidence")
    for prerequisite in lesson.prerequisites:
        _require_text(prerequisite.reference_id, "Prerequisite reference")
        _require_text(prerequisite.rationale, "Prerequisite rationale")
        if (
            prerequisite.kind is PrerequisiteKind.CONCEPT
            and prerequisite.reference_id not in concept_ids
        ):
            raise PhysicsValidationError("Concept prerequisites must reference known concepts.")
    _unique_ids(lesson.sections, "Lesson section")
    activities_by_id = {item.id: item for item in lesson.activity_sequence}
    if not activities_by_id:
        raise PhysicsValidationError("Lessons require at least one simulation activity.")
    if len(activities_by_id) != len(lesson.activity_sequence):
        raise PhysicsValidationError("Activity IDs must be unique.")
    orders = [PHASE_ORDER.index(item.phase) for item in lesson.activity_sequence]
    if orders != sorted(orders):
        raise PhysicsValidationError("Lesson activity phases must follow the learning sequence.")
    for activity in lesson.activity_sequence:
        _validate_activity(activity, lesson, simulation_ids)
    component_activities = []
    component_ids = set()
    for section in lesson.sections:
        _require_text(section.narrative, "Lesson section narrative")
        for component in section.components:
            if component.id in component_ids:
                raise PhysicsValidationError("Lesson component IDs must be unique.")
            component_ids.add(component.id)
            if isinstance(component, WorkedExample):
                _validate_worked_example(component)
            elif isinstance(component, GuidedDerivation):
                _validate_derivation(component)
            elif isinstance(component, CheckpointQuestion):
                _validate_checkpoint(component, objective_ids)
            elif isinstance(component, SimulationActivity):
                _validate_activity(component, lesson, simulation_ids)
                component_activities.append(component.id)
    if tuple(component_activities) != tuple(activities_by_id):
        raise PhysicsValidationError(
            "Section activities must appear once and match activity_sequence order."
        )


def validate_curriculum_manifest(manifest: CurriculumManifest, *, simulation_ids: set[str]) -> None:
    """Validate all references and pedagogical sequencing in a curriculum."""

    _require_text(manifest.id, "Curriculum ID")
    _require_text(manifest.version, "Curriculum version")
    _require_text(manifest.title, "Curriculum title")
    _unique_ids(manifest.subjects, "Subject")
    lesson_ids: set[str] = set()
    for subject in manifest.subjects:
        _require_text(subject.title, "Subject title")
        _require_text(subject.summary, "Subject summary")
        concept_ids = _unique_ids(subject.concepts, "Concept")
        _unique_ids(subject.units, "Unit")
        for concept in subject.concepts:
            _require_text(concept.name, "Concept name")
            _require_text(concept.definition, "Concept definition")
            if not set(concept.related_concept_ids) <= concept_ids:
                raise PhysicsValidationError("Related concepts must exist in the same subject.")
        for unit in subject.units:
            _require_text(unit.title, "Unit title")
            _require_text(unit.summary, "Unit summary")
            _unique_ids(unit.lessons, "Lesson")
            for lesson in unit.lessons:
                if lesson.id in lesson_ids:
                    raise PhysicsValidationError("Lesson IDs must be globally unique.")
                lesson_ids.add(lesson.id)
                _validate_lesson(lesson, concept_ids, simulation_ids)
            unit_objectives = {
                objective.id for lesson in unit.lessons for objective in lesson.objectives
            }
            if not set(unit.objective_ids) <= unit_objectives:
                raise PhysicsValidationError("Unit objectives must reference lesson objectives.")
    for subject in manifest.subjects:
        for unit in subject.units:
            for lesson in unit.lessons:
                for prerequisite in lesson.prerequisites:
                    if (
                        prerequisite.kind is PrerequisiteKind.LESSON
                        and prerequisite.reference_id not in lesson_ids
                    ):
                        raise PhysicsValidationError(
                            "Lesson prerequisites must reference a curriculum lesson."
                        )
