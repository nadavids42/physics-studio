"""Renderer-independent formative assessment for the Mechanics course."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from physics_playground.education.models import QuestionKind


class GradingStatus(StrEnum):
    CORRECT = "correct"
    INCORRECT = "incorrect"
    SELF_REVIEW = "self_review"


class MasteryStatus(StrEnum):
    NOT_ASSESSED = "not_assessed"
    DEVELOPING = "developing"
    DEMONSTRATED = "demonstrated"


@dataclass(frozen=True, slots=True)
class AssessmentResponse:
    """Learner input with no client-supplied correctness field."""

    selected_choice_ids: tuple[str, ...] = ()
    numeric_value: float | None = None
    unit: str = ""
    text: str = ""
    schema_version: int = 1

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "selected_choice_ids": list(self.selected_choice_ids),
            "numeric_value": self.numeric_value,
            "unit": self.unit,
            "text": self.text,
        }

    @classmethod
    def from_dict(cls, data: object) -> AssessmentResponse:
        if not isinstance(data, dict) or data.get("schema_version") != 1:
            raise ValueError("Unsupported assessment-response schema.")
        value = data.get("numeric_value")
        return cls(
            selected_choice_ids=tuple(str(item) for item in data.get("selected_choice_ids", ())),
            numeric_value=float(value) if value is not None else None,
            unit=str(data.get("unit", "")),
            text=str(data.get("text", "")),
        )


@dataclass(frozen=True, slots=True)
class VariantAnswer:
    id: str
    correct_choice_ids: tuple[str, ...] = ()
    expected_numeric_value: float | None = None


@dataclass(frozen=True, slots=True)
class MasteryRule:
    """Explicit evidence rule; activity completion is intentionally absent."""

    required_correct_attempts: int = 2
    within_most_recent_attempts: int = 3


@dataclass(frozen=True, slots=True)
class AssessmentDefinition:
    """Private scoring definition kept outside learner-visible content."""

    id: str
    lesson_id: str
    kind: QuestionKind
    objective_ids: tuple[str, ...]
    success_feedback: str
    retry_feedback: str
    correct_choice_ids: tuple[str, ...] = ()
    expected_numeric_value: float | None = None
    canonical_unit: str = ""
    absolute_tolerance: float | None = None
    relative_tolerance: float | None = None
    hints: tuple[str, ...] = ()
    remediation_lesson_ids: tuple[str, ...] = ()
    misconception_by_choice: tuple[tuple[str, str], ...] = ()
    variants: tuple[VariantAnswer, ...] = ()
    mastery_rule: MasteryRule = MasteryRule()
    schema_version: int = 2

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "lesson_id": self.lesson_id,
            "kind": self.kind.value,
            "objective_ids": list(self.objective_ids),
            "success_feedback": self.success_feedback,
            "retry_feedback": self.retry_feedback,
            "correct_choice_ids": list(self.correct_choice_ids),
            "expected_numeric_value": self.expected_numeric_value,
            "canonical_unit": self.canonical_unit,
            "absolute_tolerance": self.absolute_tolerance,
            "relative_tolerance": self.relative_tolerance,
            "hints": list(self.hints),
            "remediation_lesson_ids": list(self.remediation_lesson_ids),
            "misconception_by_choice": [list(item) for item in self.misconception_by_choice],
            "variants": [
                {
                    "id": variant.id,
                    "correct_choice_ids": list(variant.correct_choice_ids),
                    "expected_numeric_value": variant.expected_numeric_value,
                }
                for variant in self.variants
            ],
            "mastery_rule": {
                "required_correct_attempts": self.mastery_rule.required_correct_attempts,
                "within_most_recent_attempts": self.mastery_rule.within_most_recent_attempts,
            },
        }

    @classmethod
    def from_dict(cls, data: object) -> AssessmentDefinition:
        if not isinstance(data, dict) or data.get("schema_version") != 2:
            raise ValueError("Unsupported assessment-definition schema.")
        rule = data.get("mastery_rule", {})
        if not isinstance(rule, dict):
            raise ValueError("Mastery rule must be an object.")
        variants = data.get("variants", ())
        return cls(
            id=str(data["id"]),
            lesson_id=str(data["lesson_id"]),
            kind=QuestionKind(str(data["kind"])),
            objective_ids=tuple(str(item) for item in data.get("objective_ids", ())),
            success_feedback=str(data["success_feedback"]),
            retry_feedback=str(data["retry_feedback"]),
            correct_choice_ids=tuple(str(item) for item in data.get("correct_choice_ids", ())),
            expected_numeric_value=(
                float(data["expected_numeric_value"])
                if data.get("expected_numeric_value") is not None
                else None
            ),
            canonical_unit=str(data.get("canonical_unit", "")),
            absolute_tolerance=(
                float(data["absolute_tolerance"])
                if data.get("absolute_tolerance") is not None
                else None
            ),
            relative_tolerance=(
                float(data["relative_tolerance"])
                if data.get("relative_tolerance") is not None
                else None
            ),
            hints=tuple(str(item) for item in data.get("hints", ())),
            remediation_lesson_ids=tuple(
                str(item) for item in data.get("remediation_lesson_ids", ())
            ),
            misconception_by_choice=tuple(
                (str(item[0]), str(item[1]))
                for item in data.get("misconception_by_choice", ())
                if isinstance(item, list | tuple) and len(item) == 2
            ),
            variants=tuple(
                VariantAnswer(
                    str(item["id"]),
                    tuple(str(choice) for choice in item.get("correct_choice_ids", ())),
                    float(item["expected_numeric_value"])
                    if item.get("expected_numeric_value") is not None
                    else None,
                )
                for item in variants
                if isinstance(item, dict)
            ),
            mastery_rule=MasteryRule(
                int(rule.get("required_correct_attempts", 2)),
                int(rule.get("within_most_recent_attempts", 3)),
            ),
        )


@dataclass(frozen=True, slots=True)
class AssessmentAttempt:
    """Engine-produced attempt. Correctness is never accepted from the response."""

    id: str
    learner_id: str
    lesson_id: str
    assessment_id: str
    response: AssessmentResponse
    status: GradingStatus
    submitted_at: datetime
    variant_id: str = "default"
    misconception_tags: tuple[str, ...] = ()
    schema_version: int = 2

    @property
    def correct(self) -> bool:
        return self.status is GradingStatus.CORRECT

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "learner_id": self.learner_id,
            "lesson_id": self.lesson_id,
            "assessment_id": self.assessment_id,
            "response": self.response.to_dict(),
            "status": self.status.value,
            "submitted_at": self.submitted_at.astimezone(UTC).isoformat(),
            "variant_id": self.variant_id,
            "misconception_tags": list(self.misconception_tags),
        }

    @classmethod
    def from_dict(cls, data: object) -> AssessmentAttempt:
        if not isinstance(data, dict):
            raise ValueError("Assessment attempt must be an object.")
        version = int(data.get("schema_version", 1))
        if version == 1:
            return cls(
                id=str(data["id"]),
                learner_id=str(data["learner_id"]),
                lesson_id=str(data["lesson_id"]),
                assessment_id=str(data["assessment_id"]),
                response=AssessmentResponse(text=str(data.get("response", ""))),
                status=(
                    GradingStatus.CORRECT
                    if bool(data.get("correct", False))
                    else GradingStatus.INCORRECT
                ),
                submitted_at=datetime.fromisoformat(str(data["submitted_at"])),
            )
        if version != 2:
            raise ValueError("Unsupported assessment-attempt schema.")
        return cls(
            id=str(data["id"]),
            learner_id=str(data["learner_id"]),
            lesson_id=str(data["lesson_id"]),
            assessment_id=str(data["assessment_id"]),
            response=AssessmentResponse.from_dict(data["response"]),
            status=GradingStatus(str(data["status"])),
            submitted_at=datetime.fromisoformat(str(data["submitted_at"])),
            variant_id=str(data.get("variant_id", "default")),
            misconception_tags=tuple(str(item) for item in data.get("misconception_tags", ())),
        )


@dataclass(frozen=True, slots=True)
class ObjectiveEvidenceRecord:
    id: str
    learner_id: str
    lesson_id: str
    objective_id: str
    source_id: str
    source_kind: str
    recorded_at: datetime
    schema_version: int = 1

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "learner_id": self.learner_id,
            "lesson_id": self.lesson_id,
            "objective_id": self.objective_id,
            "source_id": self.source_id,
            "source_kind": self.source_kind,
            "recorded_at": self.recorded_at.astimezone(UTC).isoformat(),
        }

    @classmethod
    def from_dict(cls, data: object) -> ObjectiveEvidenceRecord:
        if not isinstance(data, dict) or data.get("schema_version") != 1:
            raise ValueError("Unsupported objective-evidence schema.")
        return cls(
            id=str(data["id"]),
            learner_id=str(data["learner_id"]),
            lesson_id=str(data["lesson_id"]),
            objective_id=str(data["objective_id"]),
            source_id=str(data["source_id"]),
            source_kind=str(data["source_kind"]),
            recorded_at=datetime.fromisoformat(str(data["recorded_at"])),
        )


@dataclass(frozen=True, slots=True)
class ObjectiveMastery:
    objective_id: str
    status: MasteryStatus
    supporting_attempt_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SubmissionResult:
    attempt: AssessmentAttempt
    feedback: str
    hint: str | None
    evidence: tuple[ObjectiveEvidenceRecord, ...]
    mastery: tuple[ObjectiveMastery, ...]


_UNIT_FACTORS: dict[str, tuple[str, float]] = {
    "m": ("length", 1.0),
    "cm": ("length", 0.01),
    "km": ("length", 1000.0),
    "s": ("time", 1.0),
    "min": ("time", 60.0),
    "m/s": ("speed", 1.0),
    "km/h": ("speed", 1.0 / 3.6),
    "m/s^2": ("acceleration", 1.0),
    "N": ("force", 1.0),
    "J": ("energy", 1.0),
    "kJ": ("energy", 1000.0),
    "kg*m/s": ("momentum", 1.0),
    "deg": ("angle", 1.0),
    "rad": ("angle", 180.0 / math.pi),
}


def convert_unit(value: float, source_unit: str, target_unit: str) -> float:
    """Convert supported Mechanics units or reject incompatible dimensions."""

    source = _UNIT_FACTORS.get(source_unit.strip())
    target = _UNIT_FACTORS.get(target_unit.strip())
    if source is None or target is None:
        raise ValueError("Unsupported unit.")
    if source[0] != target[0]:
        raise ValueError("Incompatible unit dimensions.")
    return value * source[1] / target[1]


def deterministic_variant_id(
    definition: AssessmentDefinition, *, learner_id: str, attempt_number: int
) -> str:
    if not definition.variants:
        return "default"
    material = f"{definition.id}:{learner_id}:{attempt_number}".encode()
    index = int.from_bytes(hashlib.sha256(material).digest()[:8], "big") % len(definition.variants)
    return definition.variants[index].id


def _answer_for_variant(
    definition: AssessmentDefinition, variant_id: str
) -> tuple[tuple[str, ...], float | None]:
    if variant_id == "default":
        return definition.correct_choice_ids, definition.expected_numeric_value
    variant = next((item for item in definition.variants if item.id == variant_id), None)
    if variant is None:
        raise ValueError("Unknown assessment variant.")
    return variant.correct_choice_ids, variant.expected_numeric_value


def _mastery(
    definition: AssessmentDefinition, attempts: tuple[AssessmentAttempt, ...]
) -> tuple[ObjectiveMastery, ...]:
    relevant = tuple(item for item in attempts if item.assessment_id == definition.id)
    window = relevant[-definition.mastery_rule.within_most_recent_attempts :]
    correct = tuple(item for item in window if item.status is GradingStatus.CORRECT)
    if len(correct) >= definition.mastery_rule.required_correct_attempts:
        status = MasteryStatus.DEMONSTRATED
    elif relevant:
        status = MasteryStatus.DEVELOPING
    else:
        status = MasteryStatus.NOT_ASSESSED
    return tuple(
        ObjectiveMastery(objective_id, status, tuple(item.id for item in correct))
        for objective_id in definition.objective_ids
    )


def submit_response(
    definition: AssessmentDefinition,
    response: AssessmentResponse,
    *,
    learner_id: str,
    attempt_id: str,
    submitted_at: datetime,
    prior_attempts: tuple[AssessmentAttempt, ...] = (),
    variant_id: str | None = None,
) -> SubmissionResult:
    """Grade trusted definitions against untrusted learner input."""

    selected_variant = variant_id or deterministic_variant_id(
        definition, learner_id=learner_id, attempt_number=len(prior_attempts) + 1
    )
    correct_choices, expected_numeric = _answer_for_variant(definition, selected_variant)
    status = GradingStatus.INCORRECT
    if definition.kind is QuestionKind.SHORT_RESPONSE:
        status = GradingStatus.SELF_REVIEW
    elif definition.kind is QuestionKind.NUMERIC:
        if response.numeric_value is not None and expected_numeric is not None:
            try:
                actual = convert_unit(
                    response.numeric_value, response.unit, definition.canonical_unit
                )
            except ValueError:
                actual = math.nan
            tolerance = max(
                definition.absolute_tolerance or 0.0,
                abs(expected_numeric) * (definition.relative_tolerance or 0.0),
            )
            if math.isfinite(actual) and abs(actual - expected_numeric) <= tolerance:
                status = GradingStatus.CORRECT
    elif set(response.selected_choice_ids) == set(correct_choices) and len(
        response.selected_choice_ids
    ) == len(correct_choices):
        status = GradingStatus.CORRECT

    misconception_map = dict(definition.misconception_by_choice)
    tags = tuple(
        dict.fromkeys(
            misconception_map[choice]
            for choice in response.selected_choice_ids
            if choice in misconception_map
        )
    )
    attempt = AssessmentAttempt(
        id=attempt_id,
        learner_id=learner_id,
        lesson_id=definition.lesson_id,
        assessment_id=definition.id,
        response=response,
        status=status,
        submitted_at=submitted_at,
        variant_id=selected_variant,
        misconception_tags=tags,
    )
    all_attempts = (*prior_attempts, attempt)
    evidence = (
        tuple(
            ObjectiveEvidenceRecord(
                id=f"{attempt.id}:{objective_id}",
                learner_id=learner_id,
                lesson_id=definition.lesson_id,
                objective_id=objective_id,
                source_id=attempt.id,
                source_kind="assessment",
                recorded_at=submitted_at,
            )
            for objective_id in definition.objective_ids
        )
        if status is GradingStatus.CORRECT
        else ()
    )
    attempt_count = len(tuple(item for item in all_attempts if item.assessment_id == definition.id))
    hint = (
        definition.hints[min(attempt_count - 1, len(definition.hints) - 1)]
        if status is GradingStatus.INCORRECT and definition.hints
        else None
    )
    feedback = (
        definition.success_feedback
        if status is GradingStatus.CORRECT
        else "Review your response using the provided criteria."
        if status is GradingStatus.SELF_REVIEW
        else definition.retry_feedback
    )
    return SubmissionResult(attempt, feedback, hint, evidence, _mastery(definition, all_attempts))
