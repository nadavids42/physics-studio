from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from physics_playground.education.assessments import (
    AssessmentAttempt,
    AssessmentDefinition,
    AssessmentResponse,
    GradingStatus,
    MasteryRule,
    MasteryStatus,
    VariantAnswer,
    convert_unit,
    deterministic_variant_id,
    submit_response,
)
from physics_playground.education.models import QuestionKind
from physics_playground.profiles import LocalProfile, ProfileStore

NOW = datetime(2026, 7, 18, 12, tzinfo=UTC)


def definition(kind: QuestionKind, **changes: object) -> AssessmentDefinition:
    values: dict[str, object] = {
        "id": "mechanics-check",
        "lesson_id": "mechanics-lesson",
        "kind": kind,
        "objective_ids": ("objective-1",),
        "success_feedback": "Evidence accepted.",
        "retry_feedback": "Check the physical model and retry.",
    }
    values.update(changes)
    return AssessmentDefinition(**values)  # type: ignore[arg-type]


def submit(
    item: AssessmentDefinition,
    response: AssessmentResponse,
    *,
    attempt_id: str = "attempt-1",
    prior: tuple[AssessmentAttempt, ...] = (),
    variant_id: str | None = None,
):
    return submit_response(
        item,
        response,
        learner_id="learner",
        attempt_id=attempt_id,
        submitted_at=NOW,
        prior_attempts=prior,
        variant_id=variant_id,
    )


def test_multiple_choice_and_multiple_select_require_exact_server_answer() -> None:
    choice = definition(QuestionKind.MULTIPLE_CHOICE, correct_choice_ids=("b",))
    assert submit(choice, AssessmentResponse(selected_choice_ids=("b",))).attempt.correct
    assert not submit(choice, AssessmentResponse(selected_choice_ids=("a",))).attempt.correct

    multiple = definition(QuestionKind.MULTIPLE_SELECT, correct_choice_ids=("a", "c"))
    assert submit(multiple, AssessmentResponse(selected_choice_ids=("c", "a"))).attempt.correct
    assert not submit(multiple, AssessmentResponse(selected_choice_ids=("a",))).attempt.correct
    assert not submit(
        multiple, AssessmentResponse(selected_choice_ids=("a", "b", "c"))
    ).attempt.correct


@pytest.mark.parametrize(
    ("value", "unit", "expected"),
    ((100.0, "cm", 1.0), (1.0, "km", 1000.0), (36.0, "km/h", 10.0), (3.1415926535, "rad", 180.0)),
)
def test_mechanics_unit_conversion_is_explicit(value: float, unit: str, expected: float) -> None:
    target = {"cm": "m", "km": "m", "km/h": "m/s", "rad": "deg"}[unit]
    assert convert_unit(value, unit, target) == pytest.approx(expected)


def test_unknown_missing_and_incompatible_units_do_not_grade_correct() -> None:
    numeric = definition(
        QuestionKind.NUMERIC,
        expected_numeric_value=10.0,
        canonical_unit="m/s",
        absolute_tolerance=0.1,
    )
    for response in (
        AssessmentResponse(numeric_value=10.0),
        AssessmentResponse(numeric_value=10.0, unit="furlong"),
        AssessmentResponse(numeric_value=10.0, unit="s"),
    ):
        assert submit(numeric, response).attempt.status is GradingStatus.INCORRECT


def test_numeric_tolerance_boundaries_and_false_precision() -> None:
    numeric = definition(
        QuestionKind.NUMERIC,
        expected_numeric_value=40.8,
        canonical_unit="m",
        absolute_tolerance=0.2,
        relative_tolerance=0.001,
    )
    assert submit(numeric, AssessmentResponse(numeric_value=40.6, unit="m")).attempt.correct
    assert submit(numeric, AssessmentResponse(numeric_value=4080, unit="cm")).attempt.correct
    assert not submit(numeric, AssessmentResponse(numeric_value=40.599, unit="m")).attempt.correct
    # The engine compares unrounded values using the declared tolerance; it does not
    # infer precision from the number of digits typed.
    assert submit(numeric, AssessmentResponse(numeric_value=40.8, unit="m")).attempt.correct


def test_relative_tolerance_scales_with_expected_value() -> None:
    numeric = definition(
        QuestionKind.NUMERIC,
        expected_numeric_value=1000.0,
        canonical_unit="J",
        absolute_tolerance=1.0,
        relative_tolerance=0.01,
    )
    assert submit(numeric, AssessmentResponse(numeric_value=1010.0, unit="J")).attempt.correct
    assert not submit(numeric, AssessmentResponse(numeric_value=1010.01, unit="J")).attempt.correct


def test_short_constructed_response_is_only_marked_for_self_review() -> None:
    short = definition(QuestionKind.SHORT_RESPONSE)
    result = submit(short, AssessmentResponse(text="Momentum is conserved for the system."))
    assert result.attempt.status is GradingStatus.SELF_REVIEW
    assert not result.attempt.correct
    assert not result.evidence
    assert all(item.status is MasteryStatus.DEVELOPING for item in result.mastery)


def test_retries_reveal_hints_and_preserve_attempt_history() -> None:
    item = definition(
        QuestionKind.MULTIPLE_CHOICE,
        correct_choice_ids=("b",),
        hints=("Resolve the components.", "Compare complementary angles."),
    )
    first = submit(item, AssessmentResponse(selected_choice_ids=("a",)))
    second = submit(
        item,
        AssessmentResponse(selected_choice_ids=("c",)),
        attempt_id="attempt-2",
        prior=(first.attempt,),
    )
    third = submit(
        item,
        AssessmentResponse(selected_choice_ids=("b",)),
        attempt_id="attempt-3",
        prior=(first.attempt, second.attempt),
    )
    assert first.hint == "Resolve the components."
    assert second.hint == "Compare complementary angles."
    assert third.hint is None and third.attempt.correct
    assert third.mastery[0].supporting_attempt_ids == ("attempt-3",)


def test_misconception_tags_come_from_private_definition() -> None:
    item = definition(
        QuestionKind.MULTIPLE_CHOICE,
        correct_choice_ids=("b",),
        misconception_by_choice=(("a", "velocity-is-force"),),
    )
    result = submit(item, AssessmentResponse(selected_choice_ids=("a",)))
    assert result.attempt.misconception_tags == ("velocity-is-force",)


def test_mastery_uses_explicit_recent_attempt_rule_not_action_completion() -> None:
    item = definition(
        QuestionKind.MULTIPLE_CHOICE,
        correct_choice_ids=("b",),
        mastery_rule=MasteryRule(required_correct_attempts=2, within_most_recent_attempts=3),
    )
    first = submit(item, AssessmentResponse(selected_choice_ids=("b",)))
    second = submit(
        item,
        AssessmentResponse(selected_choice_ids=("a",)),
        attempt_id="attempt-2",
        prior=(first.attempt,),
    )
    third = submit(
        item,
        AssessmentResponse(selected_choice_ids=("b",)),
        attempt_id="attempt-3",
        prior=(first.attempt, second.attempt),
    )
    assert first.mastery[0].status is MasteryStatus.DEVELOPING
    assert third.mastery[0].status is MasteryStatus.DEMONSTRATED


def test_default_mastery_rule_requires_two_correct_within_three_attempts() -> None:
    assert MasteryRule() == MasteryRule(required_correct_attempts=2, within_most_recent_attempts=3)


def test_a_single_lucky_answer_no_longer_demonstrates_mastery_by_default() -> None:
    """A 3-option multiple-choice question has a 33% guess floor; one correct
    attempt must not be enough to claim DEMONSTRATED mastery."""

    item = definition(QuestionKind.MULTIPLE_CHOICE, correct_choice_ids=("b",))
    lucky = submit(item, AssessmentResponse(selected_choice_ids=("b",)))
    assert lucky.attempt.correct
    assert lucky.mastery[0].status is MasteryStatus.DEVELOPING
    assert lucky.mastery[0].status is not MasteryStatus.DEMONSTRATED

    confirmed = submit(
        item,
        AssessmentResponse(selected_choice_ids=("b",)),
        attempt_id="attempt-2",
        prior=(lucky.attempt,),
    )
    assert confirmed.mastery[0].status is MasteryStatus.DEMONSTRATED


def test_every_catalog_assessment_is_still_achievable_under_the_default_rule() -> None:
    """A learner who keeps answering correctly must still be able to reach
    DEMONSTRATED mastery on every graded checkpoint in the shipped curriculum."""

    from physics_playground.education.catalog import ASSESSMENTS_BY_ID

    for item in ASSESSMENTS_BY_ID.values():
        if item.kind is QuestionKind.SHORT_RESPONSE:
            continue  # Self-review questions are never graded correct; excluded by design.
        assert item.mastery_rule == MasteryRule()
        attempts: list[AssessmentAttempt] = []
        result = None
        for attempt_number in range(1, item.mastery_rule.required_correct_attempts + 1):
            variant_id = deterministic_variant_id(
                item, learner_id="learner", attempt_number=attempt_number
            )
            if variant_id == "default":
                choice_ids, numeric_value = item.correct_choice_ids, item.expected_numeric_value
            else:
                variant = next(v for v in item.variants if v.id == variant_id)
                choice_ids, numeric_value = (
                    variant.correct_choice_ids,
                    variant.expected_numeric_value,
                )
            response = (
                AssessmentResponse(numeric_value=numeric_value, unit=item.canonical_unit)
                if item.kind is QuestionKind.NUMERIC
                else AssessmentResponse(selected_choice_ids=choice_ids)
            )
            result = submit(
                item,
                response,
                attempt_id=f"attempt-{attempt_number}",
                prior=tuple(attempts),
                variant_id=variant_id,
            )
            assert result.attempt.correct, f"{item.id} attempt {attempt_number} was not correct"
            attempts.append(result.attempt)
        assert result is not None
        assert all(mastery.status is MasteryStatus.DEMONSTRATED for mastery in result.mastery), (
            item.id
        )


def test_deterministic_variants_are_stable_and_server_checked() -> None:
    item = definition(
        QuestionKind.NUMERIC,
        canonical_unit="m",
        absolute_tolerance=0.1,
        variants=(
            VariantAnswer("v1", expected_numeric_value=10.0),
            VariantAnswer("v2", expected_numeric_value=20.0),
        ),
    )
    first = deterministic_variant_id(item, learner_id="learner", attempt_number=1)
    assert first == deterministic_variant_id(item, learner_id="learner", attempt_number=1)
    expected = next(value.expected_numeric_value for value in item.variants if value.id == first)
    result = submit(
        item,
        AssessmentResponse(numeric_value=expected, unit="m"),
        variant_id=first,
    )
    assert result.attempt.correct and result.attempt.variant_id == first
    with pytest.raises(ValueError, match="variant"):
        submit(item, AssessmentResponse(numeric_value=10.0, unit="m"), variant_id="client-made")


def test_definition_response_and_attempt_serialization_round_trip() -> None:
    item = definition(
        QuestionKind.NUMERIC,
        expected_numeric_value=9.81,
        canonical_unit="m/s^2",
        absolute_tolerance=0.02,
        hints=("Use SI units.",),
    )
    restored = AssessmentDefinition.from_dict(json.loads(json.dumps(item.to_dict())))
    assert restored == item
    response = AssessmentResponse(numeric_value=981.0, unit="cm")
    assert AssessmentResponse.from_dict(json.loads(json.dumps(response.to_dict()))) == response
    attempt = submit(item, AssessmentResponse(numeric_value=9.81, unit="m/s^2")).attempt
    assert AssessmentAttempt.from_dict(json.loads(json.dumps(attempt.to_dict()))) == attempt


def test_legacy_attempt_migrates_without_trusting_new_client_correctness() -> None:
    legacy = {
        "schema_version": 1,
        "id": "old",
        "learner_id": "learner",
        "lesson_id": "lesson",
        "assessment_id": "question",
        "response": "b",
        "correct": True,
        "submitted_at": NOW.isoformat(),
    }
    restored = AssessmentAttempt.from_dict(legacy)
    assert restored.correct
    assert "correct" not in AssessmentResponse().to_dict()


def test_attempt_history_and_objective_evidence_persist_separately(tmp_path) -> None:
    item = definition(QuestionKind.MULTIPLE_CHOICE, correct_choice_ids=("b",))
    result = submit(item, AssessmentResponse(selected_choice_ids=("b",)))
    profile = LocalProfile(
        "learner",
        "Learner",
        educational_progress={"mechanics-lesson": {"completed": False}},
        assessment_attempts=(result.attempt.to_dict(),),
        objective_evidence=tuple(evidence.to_dict() for evidence in result.evidence),
    )
    store = ProfileStore(tmp_path / "profiles.sqlite3")
    store.save(profile)
    restored = store.load("learner")
    assert AssessmentAttempt.from_dict(restored.assessment_attempts[0]) == result.attempt
    assert restored.educational_progress == profile.educational_progress
    assert len(restored.objective_evidence) == 1
