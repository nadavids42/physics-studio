"""Private assessment definitions and learner-owned attempts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from physics_playground.education.models import QuestionKind


@dataclass(frozen=True, slots=True)
class AssessmentDefinition:
    """Scoring data kept outside learner-visible lesson serialization."""

    id: str
    lesson_id: str
    kind: QuestionKind
    objective_ids: tuple[str, ...]
    correct_answer: str
    success_feedback: str
    hints: tuple[str, ...] = ()
    remediation_lesson_ids: tuple[str, ...] = ()
    tolerance: float | None = None
    unit: str = ""
    schema_version: int = 1

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "lesson_id": self.lesson_id,
            "kind": self.kind.value,
            "objective_ids": list(self.objective_ids),
            "correct_answer": self.correct_answer,
            "success_feedback": self.success_feedback,
            "hints": list(self.hints),
            "remediation_lesson_ids": list(self.remediation_lesson_ids),
            "tolerance": self.tolerance,
            "unit": self.unit,
        }

    @classmethod
    def from_dict(cls, data: object) -> AssessmentDefinition:
        if not isinstance(data, dict) or data.get("schema_version") != 1:
            raise ValueError("Unsupported assessment-definition schema.")
        return cls(
            id=str(data["id"]),
            lesson_id=str(data["lesson_id"]),
            kind=QuestionKind(str(data["kind"])),
            objective_ids=tuple(str(item) for item in data.get("objective_ids", ())),
            correct_answer=str(data["correct_answer"]),
            success_feedback=str(data["success_feedback"]),
            hints=tuple(str(item) for item in data.get("hints", ())),
            remediation_lesson_ids=tuple(
                str(item) for item in data.get("remediation_lesson_ids", ())
            ),
            tolerance=float(data["tolerance"]) if data.get("tolerance") is not None else None,
            unit=str(data.get("unit", "")),
        )


@dataclass(frozen=True, slots=True)
class AssessmentAttempt:
    """One learner response, separate from content, scoring policy, and progress."""

    id: str
    learner_id: str
    lesson_id: str
    assessment_id: str
    response: str
    correct: bool
    submitted_at: datetime
    schema_version: int = 1

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "learner_id": self.learner_id,
            "lesson_id": self.lesson_id,
            "assessment_id": self.assessment_id,
            "response": self.response,
            "correct": self.correct,
            "submitted_at": self.submitted_at.astimezone(UTC).isoformat(),
        }

    @classmethod
    def from_dict(cls, data: object) -> AssessmentAttempt:
        if not isinstance(data, dict) or data.get("schema_version") != 1:
            raise ValueError("Unsupported assessment-attempt schema.")
        return cls(
            id=str(data["id"]),
            learner_id=str(data["learner_id"]),
            lesson_id=str(data["lesson_id"]),
            assessment_id=str(data["assessment_id"]),
            response=str(data["response"]),
            correct=bool(data["correct"]),
            submitted_at=datetime.fromisoformat(str(data["submitted_at"])),
        )


@dataclass(frozen=True, slots=True)
class ObjectiveEvidenceRecord:
    """Evidence for one objective, stored separately from pathway progress."""

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


def evaluate_response(definition: AssessmentDefinition, response: str) -> bool:
    """Evaluate the currently supported multiple-choice and numeric answers."""

    if definition.kind is QuestionKind.NUMERIC:
        try:
            actual = float(response)
            expected = float(definition.correct_answer)
        except ValueError:
            return False
        return abs(actual - expected) <= (definition.tolerance or 0.0)
    return response.strip() == definition.correct_answer
