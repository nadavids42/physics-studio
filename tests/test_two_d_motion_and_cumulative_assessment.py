"""Structure and grading-behavior tests for the 2D motion bridge lesson and the
cumulative assessment (Prompt 11). Assertions target counts, provenance, and
engine grading outcomes rather than exact question phrasing."""

from datetime import UTC, datetime

from physics_playground.education.assessments import (
    AssessmentDefinition,
    AssessmentResponse,
    GradingStatus,
    MasteryRule,
    MasteryStatus,
    SubmissionResult,
    submit_response,
)
from physics_playground.education.catalog import ASSESSMENTS_BY_ID
from physics_playground.education.models import CheckpointQuestion, PrerequisiteKind, QuestionKind
from physics_playground.education.progress import PathwayProgress, prerequisites_satisfied
from physics_playground.subjects.mechanics.cannonball.lesson import CANNONBALL_LESSON
from physics_playground.subjects.mechanics.cumulative_assessment import (
    CUMULATIVE_ASSESSMENT_LESSON,
    CUMULATIVE_ASSESSMENTS,
)
from physics_playground.subjects.mechanics.kinematics_lessons import (
    CONSTANT_LESSON,
    GRAPH_LESSON,
    POSITION_LESSON,
    VECTORS_LESSON,
)
from physics_playground.subjects.mechanics.two_d_motion_lesson import (
    TWO_D_MOTION_LESSON,
)


def _grade(definition: AssessmentDefinition, response: AssessmentResponse) -> SubmissionResult:
    return submit_response(
        definition,
        response,
        learner_id="learner",
        attempt_id="attempt",
        submitted_at=datetime.now(UTC),
    )


def _checkpoints(lesson) -> tuple[CheckpointQuestion, ...]:
    return tuple(
        item
        for section in lesson.sections
        for item in section.components
        if isinstance(item, CheckpointQuestion)
    )


# --- 2D motion bridge lesson structure -------------------------------------------------


def test_two_d_motion_sits_between_vectors_and_projectile_motion() -> None:
    assert VECTORS_LESSON.next_lesson_id == TWO_D_MOTION_LESSON.id
    assert TWO_D_MOTION_LESSON.next_lesson_id == CANNONBALL_LESSON.id
    lesson_prerequisites = [
        item for item in TWO_D_MOTION_LESSON.prerequisites if item.kind is PrerequisiteKind.LESSON
    ]
    assert len(lesson_prerequisites) == 1
    assert lesson_prerequisites[0].reference_id == VECTORS_LESSON.id
    assert lesson_prerequisites[0].required


def test_two_d_motion_uses_the_cannonball_simulation_for_its_activity() -> None:
    assert TWO_D_MOTION_LESSON.simulation_ids == ("cannonball",)
    assert all(
        activity.simulation_id == "cannonball" for activity in TWO_D_MOTION_LESSON.activity_sequence
    )


def test_two_d_motion_worked_example_combines_constant_velocity_x_with_accelerated_y() -> None:
    components = [item for section in TWO_D_MOTION_LESSON.sections for item in section.components]
    example = next(
        item
        for item in components
        if hasattr(item, "known_values") and getattr(item, "id", "") == "m07-combine-example"
    )
    known_symbols = {known.quantity.symbol for known in example.known_values}
    assert {"v_x", "v_y0", "a_y", "t"} <= known_symbols
    # One reasoning step must be a pure constant-velocity relation (no acceleration term)
    # and another must be the constant-acceleration relation, i.e. two distinct 1D models.
    expressions = [step.expression for step in example.symbolic_reasoning]
    assert any(expr.strip().startswith("x = v_x") for expr in expressions)
    assert any("a_y" in expr for expr in expressions)


def test_two_d_motion_checkpoint_grades_correctly_with_the_existing_engine() -> None:
    definition = ASSESSMENTS_BY_ID["m07-position-check"]
    assert definition.mastery_rule == MasteryRule()
    correct = _grade(definition, AssessmentResponse(numeric_value=-0.78, unit="m"))
    assert correct.attempt.status is GradingStatus.CORRECT
    wrong = _grade(definition, AssessmentResponse(numeric_value=0.78, unit="m"))
    assert wrong.attempt.status is GradingStatus.INCORRECT


# --- Cumulative assessment structure -----------------------------------------------


def test_cumulative_check_has_six_to_eight_items_at_least_half_numeric() -> None:
    checkpoints = _checkpoints(CUMULATIVE_ASSESSMENT_LESSON)
    assert 6 <= len(checkpoints) <= 8
    numeric = [item for item in checkpoints if item.kind is QuestionKind.NUMERIC]
    assert len(numeric) * 2 >= len(checkpoints)
    assert {item.id for item in checkpoints} == {item.id for item in CUMULATIVE_ASSESSMENTS}


def test_cumulative_check_draws_on_at_least_four_distinct_lessons() -> None:
    """Each concept the check references must be owned by a distinct earlier lesson."""

    source_lessons = (
        POSITION_LESSON,
        GRAPH_LESSON,
        CONSTANT_LESSON,
        VECTORS_LESSON,
        TWO_D_MOTION_LESSON,
        CANNONBALL_LESSON,
    )
    contributing_lessons = {
        lesson.id
        for concept_id in CUMULATIVE_ASSESSMENT_LESSON.concept_ids
        for lesson in source_lessons
        if concept_id in lesson.concept_ids
    }
    assert len(contributing_lessons) >= 4


def test_cumulative_check_requires_the_full_sequence_completed_first() -> None:
    partial = {
        POSITION_LESSON.id: PathwayProgress(POSITION_LESSON.id, completed=True),
        TWO_D_MOTION_LESSON.id: PathwayProgress(TWO_D_MOTION_LESSON.id, completed=True),
    }
    assert not prerequisites_satisfied(CUMULATIVE_ASSESSMENT_LESSON, partial)

    complete = {
        **partial,
        CANNONBALL_LESSON.id: PathwayProgress(CANNONBALL_LESSON.id, completed=True),
    }
    assert prerequisites_satisfied(CUMULATIVE_ASSESSMENT_LESSON, complete)


def test_cumulative_check_items_use_the_default_mastery_rule() -> None:
    for definition in CUMULATIVE_ASSESSMENTS:
        assert definition.mastery_rule == MasteryRule()
        assert definition.mastery_rule.required_correct_attempts == 2
        assert definition.mastery_rule.within_most_recent_attempts == 3


def test_cumulative_check_grades_each_item_correctly_and_incorrectly() -> None:
    expectations = {
        "cum-velocity-check": (AssessmentResponse(numeric_value=3.0, unit="m/s"), True),
        "cum-velocity-check-wrong": (AssessmentResponse(numeric_value=-3.0, unit="m/s"), False),
        "cum-acceleration-check": (AssessmentResponse(numeric_value=-3.0, unit="m/s^2"), True),
        "cum-stopping-distance-check": (AssessmentResponse(numeric_value=8.0, unit="m"), True),
        "cum-components-check": (AssessmentResponse(numeric_value=5.0, unit="m/s"), True),
        "cum-two-d-position-check": (AssessmentResponse(numeric_value=1.06, unit="m"), True),
        "cum-model-limits-check": (
            AssessmentResponse(selected_choice_ids=("range-changes",)),
            True,
        ),
        "cum-model-limits-check-wrong": (
            AssessmentResponse(selected_choice_ids=("angle-changes",)),
            False,
        ),
        "cum-independence-check": (AssessmentResponse(selected_choice_ids=("same-time",)), True),
    }
    for key, (response, expected_correct) in expectations.items():
        definition_id = key.replace("-wrong", "")
        definition = ASSESSMENTS_BY_ID[definition_id]
        result = _grade(definition, response)
        assert result.attempt.correct is expected_correct


def test_cumulative_check_mastery_demonstrated_only_after_two_correct_of_last_three() -> None:
    definition = ASSESSMENTS_BY_ID["cum-velocity-check"]
    wrong = AssessmentResponse(numeric_value=0.0, unit="m/s")
    right = AssessmentResponse(numeric_value=3.0, unit="m/s")

    attempts: tuple = ()
    for index, response in enumerate((wrong, right, right)):
        result = submit_response(
            definition,
            response,
            learner_id="learner",
            attempt_id=f"attempt-{index}",
            submitted_at=datetime.now(UTC),
            prior_attempts=attempts,
        )
        attempts = (*attempts, result.attempt)
        mastery_by_objective = {item.objective_id: item.status for item in result.mastery}

    assert mastery_by_objective["cum-velocity"] is MasteryStatus.DEMONSTRATED


def test_free_text_reflection_alone_cannot_complete_the_cumulative_check() -> None:
    activity = CUMULATIVE_ASSESSMENT_LESSON.activity_sequence[0]
    progress = PathwayProgress(CUMULATIVE_ASSESSMENT_LESSON.id)
    required_activities = tuple(item.id for item in CUMULATIVE_ASSESSMENT_LESSON.activity_sequence)
    required_checkpoints = tuple(item.id for item in _checkpoints(CUMULATIVE_ASSESSMENT_LESSON))
    progress = progress.save_activity_response(
        activity.id,
        "This run showed the range symmetry idea from the course.",
        required_activity_ids=required_activities,
        required_checkpoint_ids=required_checkpoints,
    )
    assert not progress.completed
    assert not progress.mastered_objective_ids
