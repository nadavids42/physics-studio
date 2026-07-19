from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime

import pytest

from physics_playground.education.assessments import (
    AssessmentAttempt,
    AssessmentDefinition,
    AssessmentResponse,
    GradingStatus,
    submit_response,
)
from physics_playground.education.catalog import ASSESSMENTS, CURRICULUM
from physics_playground.education.models import (
    CheckpointQuestion,
    Prerequisite,
    PrerequisiteKind,
)
from physics_playground.education.progress import PathwayProgress, prerequisites_satisfied
from physics_playground.education.validation import validate_curriculum_manifest
from physics_playground.registry import SIMULATION_REGISTRY
from physics_playground.subjects.mechanics.cannonball.lesson import (
    CANNONBALL_ASSESSMENTS,
    CANNONBALL_LESSON,
)
from physics_playground.validation import PhysicsValidationError

SIMULATION_IDS = {simulation.id for simulation in SIMULATION_REGISTRY}


def checkpoint() -> CheckpointQuestion:
    return next(
        component
        for section in CANNONBALL_LESSON.sections
        for component in section.components
        if isinstance(component, CheckpointQuestion)
    )


def test_learner_visible_content_round_trip_excludes_answer_data() -> None:
    original = checkpoint()
    payload = original.to_dict()
    encoded = json.dumps(payload)
    assert CheckpointQuestion.from_dict(json.loads(encoded)) == original
    assert "correct_answer" not in encoded
    assert "success_feedback" not in encoded
    assert payload["schema_version"] == 1


def test_assessment_definition_and_attempt_round_trip_separately() -> None:
    definition = CANNONBALL_ASSESSMENTS[0]
    assert (
        AssessmentDefinition.from_dict(json.loads(json.dumps(definition.to_dict()))) == definition
    )

    first_result = submit_response(
        definition,
        AssessmentResponse(selected_choice_ids=("angle-45",)),
        learner_id="learner",
        attempt_id="attempt-1",
        submitted_at=datetime(2026, 7, 18, 12, tzinfo=UTC),
    )
    first = first_result.attempt
    second = replace(
        first,
        id="attempt-2",
        response=AssessmentResponse(selected_choice_ids=("angle-60",)),
        status=GradingStatus.CORRECT,
    )
    assert AssessmentAttempt.from_dict(json.loads(json.dumps(first.to_dict()))) == first
    assert AssessmentAttempt.from_dict(json.loads(json.dumps(second.to_dict()))) == second
    assert not first.correct
    assert second.correct


def test_saved_v1_progress_migrates_and_v3_round_trips() -> None:
    legacy = {
        "lesson_id": CANNONBALL_LESSON.id,
        "completed_activity_ids": ["predict-angle"],
        "completed_checkpoint_ids": [],
        "prediction": "45 degrees",
        "reflection": None,
        "completed": False,
    }
    migrated = PathwayProgress.from_dict(legacy, lesson_id=CANNONBALL_LESSON.id)
    assert migrated.schema_version == 3
    assert migrated.completed_activity_ids == ("predict-angle",)
    assert migrated.mastered_objective_ids == ()
    assert (
        PathwayProgress.from_dict(
            json.loads(json.dumps(migrated.to_dict())), lesson_id=CANNONBALL_LESSON.id
        )
        == migrated
    )


def test_successful_attempt_updates_progress_without_embedding_attempt() -> None:
    progress = PathwayProgress(CANNONBALL_LESSON.id).complete_checkpoint(
        "range-checkpoint",
        required_activity_ids=(),
        required_checkpoint_ids=("range-checkpoint",),
        objective_ids=("projectile-range",),
        attempt_id="attempt-2",
    )
    assert progress.completed
    assert progress.mastered_objective_ids == ()
    assert progress.assessment_attempt_ids == ("attempt-2",)
    assert "response" not in progress.to_dict()


def test_prerequisite_mastery_is_derived_from_separate_progress() -> None:
    prerequisite = Prerequisite(
        "prior-lesson",
        PrerequisiteKind.LESSON,
        "prior",
        "Prior lesson mastery is required.",
    )
    lesson = replace(CANNONBALL_LESSON, prerequisites=(prerequisite,))
    assert not prerequisites_satisfied(lesson, {})
    assert not prerequisites_satisfied(lesson, {"prior": PathwayProgress("prior")})
    assert prerequisites_satisfied(lesson, {"prior": PathwayProgress("prior", completed=True)})


def test_private_answer_definition_is_validated_against_visible_choices() -> None:
    range_definition = next(
        item for item in CANNONBALL_ASSESSMENTS if item.id == "range-checkpoint"
    )
    invalid = replace(range_definition, correct_choice_ids=("missing",))
    definitions = tuple(invalid if item.id == invalid.id else item for item in ASSESSMENTS)
    with pytest.raises(PhysicsValidationError, match="choice"):
        validate_curriculum_manifest(
            CURRICULUM, simulation_ids=SIMULATION_IDS, assessments=definitions
        )


def test_cannonball_content_and_private_assessment_migrate_together() -> None:
    validate_curriculum_manifest(CURRICULUM, simulation_ids=SIMULATION_IDS, assessments=ASSESSMENTS)
    visible = checkpoint()
    private = next(item for item in CANNONBALL_ASSESSMENTS if item.id == visible.id)
    assert set(visible.objective_ids) == set(private.objective_ids)
