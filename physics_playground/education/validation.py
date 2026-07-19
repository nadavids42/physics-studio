"""Validation gates for curriculum manifests and lesson sequencing."""

from __future__ import annotations

import math
from collections.abc import Iterable

from physics_playground.education.assessments import AssessmentDefinition, convert_unit
from physics_playground.education.models import (
    ALL_MATHEMATICAL_DEPTHS,
    ActivityPhase,
    CheckpointQuestion,
    CurriculumManifest,
    DiagramSpec,
    GuidedDerivation,
    Lesson,
    PrerequisiteKind,
    QuestionKind,
    SimulationActivity,
    WorkedExample,
)
from physics_playground.models.simulations import LearningMode
from physics_playground.validation import PhysicsValidationError

PHASE_ORDER = tuple(ActivityPhase)
EXPECTED_MODES = {
    ActivityPhase.PREDICTION: LearningMode.EXPLORE,
    ActivityPhase.EXPLORATION: LearningMode.EXPLORE,
    ActivityPhase.COMPARISON: LearningMode.COMPARE,
    ActivityPhase.ANALYSIS: LearningMode.ANALYZE,
    ActivityPhase.MODELING: LearningMode.MODEL,
}


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise PhysicsValidationError(f"{label} cannot be blank.")


def _require_depths(item: object, label: str) -> None:
    # Content authored before audience profiles had no depth field and is valid at every
    # depth. Keep that compatibility distinct from an explicitly empty declaration.
    declared = getattr(item, "applicable_depths", ALL_MATHEMATICAL_DEPTHS)
    if not declared:
        item_id = getattr(item, "id", "unknown")
        raise PhysicsValidationError(
            f"{label} {item_id!r} must apply to at least one mathematical depth."
        )


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
    if question.schema_version != 1:
        raise PhysicsValidationError("Unsupported checkpoint content schema.")
    if not question.objective_ids or not set(question.objective_ids) <= objective_ids:
        raise PhysicsValidationError("Checkpoint objectives must reference lesson objectives.")
    if (
        question.kind in {QuestionKind.MULTIPLE_CHOICE, QuestionKind.MULTIPLE_SELECT}
        and len(_unique_ids(question.choices, "Answer choice")) < 2
    ):
        raise PhysicsValidationError("Choice checkpoints need at least two choices.")
    variant_ids = _unique_ids(question.variants, "Question variant")
    for variant in question.variants:
        _require_text(variant.prompt, "Question variant prompt")
        if (
            question.kind in {QuestionKind.MULTIPLE_CHOICE, QuestionKind.MULTIPLE_SELECT}
            and len(_unique_ids(variant.choices, "Variant answer choice")) < 2
        ):
            raise PhysicsValidationError("Choice variants need at least two choices.")
        if question.kind is QuestionKind.NUMERIC and not variant.unit_options:
            raise PhysicsValidationError("Numeric variants require unit options.")
    if len(variant_ids) != len(question.variants):
        raise PhysicsValidationError("Question variant IDs must be unique.")


def _validate_activity(
    activity: SimulationActivity, lesson: Lesson, simulation_ids: set[str]
) -> None:
    if activity.simulation_id not in simulation_ids:
        raise PhysicsValidationError(f"Unknown simulation reference: {activity.simulation_id}.")
    if activity.simulation_id not in lesson.simulation_ids:
        raise PhysicsValidationError(
            "Activities must reference a simulation declared by the lesson."
        )
    objective_ids = {objective.id for objective in lesson.objectives}
    if not activity.objective_ids or not set(activity.objective_ids) <= objective_ids:
        raise PhysicsValidationError("Activities must reference lesson objectives.")
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
    if not set(lesson.simulation_ids) <= simulation_ids:
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
    if len(activities_by_id) != len(lesson.activity_sequence):
        raise PhysicsValidationError("Activity IDs must be unique.")
    orders = [PHASE_ORDER.index(item.phase) for item in lesson.activity_sequence]
    if orders != sorted(orders):
        raise PhysicsValidationError("Lesson activity phases must follow the learning sequence.")
    for activity in lesson.activity_sequence:
        _validate_activity(activity, lesson, simulation_ids)
    component_activities = []
    component_ids = set()
    covered_objective_ids: set[str] = set()
    for section in lesson.sections:
        _require_depths(section, "Lesson section")
        _require_text(section.narrative, "Lesson section narrative")
        for component in section.components:
            _require_depths(component, "Lesson component")
            if component.id in component_ids:
                raise PhysicsValidationError("Lesson component IDs must be unique.")
            component_ids.add(component.id)
            if isinstance(component, WorkedExample):
                _validate_worked_example(component)
            elif isinstance(component, GuidedDerivation):
                _validate_derivation(component)
            elif isinstance(component, CheckpointQuestion):
                _validate_checkpoint(component, objective_ids)
                covered_objective_ids.update(component.objective_ids)
            elif isinstance(component, DiagramSpec):
                if (
                    component.schema_version != 1
                    or not component.asset_id
                    or not component.alt_text
                ):
                    raise PhysicsValidationError(
                        "Diagrams require a supported schema, asset, and alt text."
                    )
                if not component.objective_ids or not set(component.objective_ids) <= objective_ids:
                    raise PhysicsValidationError("Diagrams must reference lesson objectives.")
                covered_objective_ids.update(component.objective_ids)
            elif isinstance(component, SimulationActivity):
                _validate_activity(component, lesson, simulation_ids)
                component_activities.append(component.id)
                covered_objective_ids.update(component.objective_ids)
    if tuple(component_activities) != tuple(activities_by_id):
        raise PhysicsValidationError(
            "Section activities must appear once and match activity_sequence order."
        )
    if covered_objective_ids != objective_ids:
        raise PhysicsValidationError("Lesson components must cover every learning objective.")


def _validate_assessments(
    definitions: tuple[AssessmentDefinition, ...],
    lessons_by_id: dict[str, Lesson],
) -> None:
    definition_ids = _unique_ids(definitions, "Assessment definition")
    checkpoints = {
        component.id: (lesson, component)
        for lesson in lessons_by_id.values()
        for section in lesson.sections
        for component in section.components
        if isinstance(component, CheckpointQuestion)
    }
    if definition_ids != set(checkpoints):
        raise PhysicsValidationError("Assessment definitions must exactly match checkpoints.")
    for definition in definitions:
        if definition.schema_version != 2 or definition.lesson_id not in lessons_by_id:
            raise PhysicsValidationError("Assessment definition has an invalid schema or lesson.")
        lesson, question = checkpoints[definition.id]
        if lesson.id != definition.lesson_id or question.kind is not definition.kind:
            raise PhysicsValidationError("Assessment definition does not match checkpoint content.")
        if set(definition.objective_ids) != set(question.objective_ids):
            raise PhysicsValidationError("Assessment objectives must match checkpoint objectives.")
        if not definition.success_feedback or not definition.retry_feedback:
            raise PhysicsValidationError("Assessment definitions require feedback.")
        public_variants = {item.id: item for item in question.variants}
        private_variants = {item.id: item for item in definition.variants}
        if set(public_variants) != set(private_variants):
            raise PhysicsValidationError("Public and private question variants must match.")
        choice_ids = {choice.id for choice in question.choices}
        if definition.kind in {QuestionKind.MULTIPLE_CHOICE, QuestionKind.MULTIPLE_SELECT} and (
            not definition.correct_choice_ids
            or not set(definition.correct_choice_ids) <= choice_ids
        ):
            raise PhysicsValidationError("Choice answers must reference visible choices.")
        for variant_id, answer in private_variants.items():
            visible = public_variants[variant_id]
            visible_choice_ids = {choice.id for choice in visible.choices}
            if definition.kind in {
                QuestionKind.MULTIPLE_CHOICE,
                QuestionKind.MULTIPLE_SELECT,
            } and (
                not answer.correct_choice_ids
                or not set(answer.correct_choice_ids) <= visible_choice_ids
            ):
                raise PhysicsValidationError("Variant answers must reference visible choices.")
        if definition.kind is QuestionKind.NUMERIC and (
            (definition.expected_numeric_value is None and not definition.variants)
            or any(item.expected_numeric_value is None for item in definition.variants)
            or (
                definition.expected_numeric_value is not None
                and not math.isfinite(definition.expected_numeric_value)
            )
            or any(
                item.expected_numeric_value is not None
                and not math.isfinite(item.expected_numeric_value)
                for item in definition.variants
            )
            or (definition.absolute_tolerance is None and definition.relative_tolerance is None)
            or (definition.absolute_tolerance or 0) < 0
            or (definition.relative_tolerance or 0) < 0
            or not definition.canonical_unit.strip()
            or not question.unit_options
        ):
            raise PhysicsValidationError("Numeric answers require tolerance and units.")
        if definition.kind is QuestionKind.NUMERIC:
            try:
                for unit in question.unit_options:
                    convert_unit(1.0, unit, definition.canonical_unit)
                for variant in question.variants:
                    for unit in variant.unit_options:
                        convert_unit(1.0, unit, definition.canonical_unit)
            except ValueError as error:
                raise PhysicsValidationError(
                    "Numeric response units must be supported and dimensionally compatible."
                ) from error
        if definition.kind is QuestionKind.SHORT_RESPONSE and (
            definition.correct_choice_ids or definition.expected_numeric_value is not None
        ):
            raise PhysicsValidationError("Short responses must be marked for self-review.")
        if (
            definition.mastery_rule.required_correct_attempts <= 0
            or definition.mastery_rule.within_most_recent_attempts
            < definition.mastery_rule.required_correct_attempts
        ):
            raise PhysicsValidationError("Mastery rules require a valid explicit attempt window.")
        if not set(definition.remediation_lesson_ids) <= set(lessons_by_id):
            raise PhysicsValidationError("Assessment remediation must reference known lessons.")


def validate_curriculum_manifest(
    manifest: CurriculumManifest,
    *,
    simulation_ids: set[str],
    assessments: tuple[AssessmentDefinition, ...],
) -> None:
    """Validate all references and pedagogical sequencing in a curriculum."""

    _require_text(manifest.id, "Curriculum ID")
    _require_text(manifest.version, "Curriculum version")
    _require_text(manifest.title, "Curriculum title")
    if manifest.schema_version != 1:
        raise PhysicsValidationError("Unsupported curriculum content schema.")
    _unique_ids(manifest.subjects, "Subject")
    lesson_ids: set[str] = set()
    lessons_by_id: dict[str, Lesson] = {}
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
                lessons_by_id[lesson.id] = lesson
                _validate_lesson(lesson, concept_ids, simulation_ids)
            unit_objectives = {
                objective.id for lesson in unit.lessons for objective in lesson.objectives
            }
            if (
                len(unit.objective_ids) != len(set(unit.objective_ids))
                or set(unit.objective_ids) != unit_objectives
            ):
                raise PhysicsValidationError(
                    "Unit expectations must reference every lesson objective exactly once."
                )
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
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(lesson_id: str) -> None:
        if lesson_id in visiting:
            raise PhysicsValidationError("Lesson prerequisite graph contains a cycle.")
        if lesson_id in visited:
            return
        visiting.add(lesson_id)
        for prerequisite in lessons_by_id[lesson_id].prerequisites:
            if prerequisite.kind is PrerequisiteKind.LESSON:
                visit(prerequisite.reference_id)
        visiting.remove(lesson_id)
        visited.add(lesson_id)

    for lesson_id in lesson_ids:
        visit(lesson_id)
    _validate_assessments(assessments, lessons_by_id)
