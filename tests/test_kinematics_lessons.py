"""Coverage, progression, science, and evidence tests for kinematics lessons."""

from datetime import UTC, datetime

from physics_playground.education.assessments import (
    AssessmentDefinition,
    AssessmentResponse,
    SubmissionResult,
    submit_response,
)
from physics_playground.education.catalog import ASSESSMENTS_BY_ID
from physics_playground.education.models import (
    CheckpointQuestion,
    GuidedDerivation,
    MisconceptionCallout,
    PrerequisiteKind,
    SimulationActivity,
    WorkedExample,
)
from physics_playground.education.progress import PathwayProgress, prerequisites_satisfied
from physics_playground.subjects.mechanics.cannonball.lesson import CANNONBALL_LESSON
from physics_playground.subjects.mechanics.kinematics_lessons import (
    CONSTANT_LESSON,
    KINEMATICS_LESSONS,
    VECTORS_LESSON,
)


def test_kinematics_prerequisites_form_one_progression_from_lesson_one() -> None:
    expected = (
        "m01-measurement-models",
        KINEMATICS_LESSONS[0].id,
        KINEMATICS_LESSONS[1].id,
        KINEMATICS_LESSONS[2].id,
    )
    assert tuple(lesson.prerequisites[0].reference_id for lesson in KINEMATICS_LESSONS) == expected
    assert any(
        prerequisite.reference_id == KINEMATICS_LESSONS[-1].id
        for prerequisite in CANNONBALL_LESSON.prerequisites
    )


def test_sequence_uses_multiple_simulations_and_complete_scientific_components() -> None:
    assert {lesson.simulation_ids[0] for lesson in KINEMATICS_LESSONS} == {
        "bumper_cars",
        "cannonball",
        "inclined_plane",
    }
    for lesson in KINEMATICS_LESSONS:
        components = [item for section in lesson.sections for item in section.components]
        assert any(isinstance(item, WorkedExample) for item in components)
        assert any(isinstance(item, MisconceptionCallout) for item in components)
        assert any(isinstance(item, CheckpointQuestion) for item in components)
        assert any(isinstance(item, SimulationActivity) for item in components)
        assert "m/s" in " ".join(
            item.unit_check for item in components if isinstance(item, WorkedExample)
        )


def test_every_objective_has_component_evidence_and_every_checkpoint_has_scoring() -> None:
    for lesson in KINEMATICS_LESSONS:
        objective_ids = {objective.id for objective in lesson.objectives}
        covered: set[str] = set()
        for section in lesson.sections:
            for component in section.components:
                if isinstance(component, SimulationActivity | CheckpointQuestion):
                    covered.update(component.objective_ids)
                if isinstance(component, CheckpointQuestion):
                    definition = ASSESSMENTS_BY_ID[component.id]
                    assert definition.lesson_id == lesson.id
                    assert set(definition.objective_ids) == set(component.objective_ids)
        assert covered == objective_ids


def test_required_misconceptions_are_explicitly_diagnosed() -> None:
    text = " ".join(
        item.misconception
        for lesson in (*KINEMATICS_LESSONS, CANNONBALL_LESSON)
        for section in lesson.sections
        for item in section.components
        if isinstance(item, MisconceptionCallout)
    ).lower()
    for phrase in (
        "negative velocity means",
        "zero velocity means zero acceleration",
        "heavier projectiles fall faster",
        "acceleration always points in the direction of motion",
        "45° launch always",
    ):
        assert phrase in text


def test_constant_acceleration_is_derived_and_assessed_quantitatively() -> None:
    constant_lesson = CONSTANT_LESSON
    components = [item for section in constant_lesson.sections for item in section.components]
    derivation = next(item for item in components if isinstance(item, GuidedDerivation))
    assert len(derivation.steps) == 4
    assert "v^2=v_0^2+2a delta x" in derivation.steps[-1].expression
    definition = ASSESSMENTS_BY_ID["m05-stopping-distance-check"]
    assert definition.expected_numeric_value == 25.0
    assert definition.canonical_unit == "m"


def test_vectors_lesson_precedes_and_is_a_hard_prerequisite_for_projectile_motion() -> None:
    # The lesson must exist and sit immediately before projectile motion in sequence.
    assert VECTORS_LESSON in KINEMATICS_LESSONS
    assert KINEMATICS_LESSONS[-1] is VECTORS_LESSON
    assert CONSTANT_LESSON.next_lesson_id == VECTORS_LESSON.id
    assert VECTORS_LESSON.next_lesson_id == CANNONBALL_LESSON.id

    # It must gate projectile motion as a required LESSON prerequisite, not an
    # unenforced SKILL reference.
    trig_prerequisite = next(
        item for item in CANNONBALL_LESSON.prerequisites if item.reference_id == VECTORS_LESSON.id
    )
    assert trig_prerequisite.kind is PrerequisiteKind.LESSON
    assert trig_prerequisite.required
    assert not any(
        item.kind is PrerequisiteKind.SKILL and "trigonometry" in item.reference_id
        for item in CANNONBALL_LESSON.prerequisites
    )

    checkpoint_ids = {
        item.id
        for section in CANNONBALL_LESSON.sections
        for item in section.components
        if isinstance(item, CheckpointQuestion)
    }
    assert {"component-checkpoint", "range-checkpoint", "model-limit-checkpoint"} <= checkpoint_ids


def test_a_learner_who_has_not_completed_vectors_is_blocked_from_projectile_motion() -> None:
    constant_only = {CONSTANT_LESSON.id: PathwayProgress(CONSTANT_LESSON.id, completed=True)}
    assert not prerequisites_satisfied(CANNONBALL_LESSON, constant_only)

    with_vectors = {
        **constant_only,
        VECTORS_LESSON.id: PathwayProgress(VECTORS_LESSON.id, completed=True),
    }
    assert prerequisites_satisfied(CANNONBALL_LESSON, with_vectors)


def test_new_quantitative_evidence_requires_correct_sign_value_and_unit() -> None:
    def grade(definition: AssessmentDefinition, response: AssessmentResponse) -> SubmissionResult:
        return submit_response(
            definition,
            response,
            learner_id="learner",
            attempt_id="attempt",
            submitted_at=datetime.now(UTC),
        )

    acceleration = ASSESSMENTS_BY_ID["m03-acceleration-check"]
    assert grade(acceleration, AssessmentResponse(numeric_value=-2.0, unit="m/s^2")).attempt.correct
    assert not grade(
        acceleration, AssessmentResponse(numeric_value=2.0, unit="m/s^2")
    ).attempt.correct
    stopping = ASSESSMENTS_BY_ID["m05-stopping-distance-check"]
    assert grade(stopping, AssessmentResponse(numeric_value=2500, unit="cm")).attempt.correct

    vy_check = ASSESSMENTS_BY_ID["m06-vy-check"]
    assert grade(vy_check, AssessmentResponse(numeric_value=8.0, unit="m/s")).attempt.correct
    assert not grade(vy_check, AssessmentResponse(numeric_value=16.0, unit="m/s")).attempt.correct
    vx_check = ASSESSMENTS_BY_ID["m06-vx-check"]
    assert grade(vx_check, AssessmentResponse(numeric_value=8.0, unit="m/s")).attempt.correct
    assert not grade(vx_check, AssessmentResponse(numeric_value=13.86, unit="m/s")).attempt.correct


def test_visiting_or_opening_a_simulation_cannot_complete_a_lesson() -> None:
    for lesson in KINEMATICS_LESSONS:
        progress = PathwayProgress(lesson.id)
        assert not progress.completed
        assert not progress.completed_activity_ids
        assert not progress.mastered_objective_ids
        evidence_activities = [item for item in lesson.activity_sequence if item.evidence_prompt]
        assert evidence_activities
        for activity in evidence_activities:
            try:
                progress.save_activity_response(
                    activity.id,
                    " ",
                    required_activity_ids=tuple(item.id for item in lesson.activity_sequence),
                    required_checkpoint_ids=(),
                )
            except ValueError:
                pass
            else:
                raise AssertionError("Blank evidence must not complete an activity")
