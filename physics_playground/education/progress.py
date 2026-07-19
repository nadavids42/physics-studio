"""Pure progress operations for lesson pathways."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Any

from physics_playground.education.models import Lesson, PrerequisiteKind


@dataclass(frozen=True, slots=True)
class PathwayProgress:
    lesson_id: str
    completed_activity_ids: tuple[str, ...] = ()
    completed_checkpoint_ids: tuple[str, ...] = ()
    prediction: str | None = None
    reflection: str | None = None
    completed: bool = False
    mastered_objective_ids: tuple[str, ...] = ()
    assessment_attempt_ids: tuple[str, ...] = ()
    completed_section_ids: tuple[str, ...] = ()
    last_section_id: str | None = None
    activity_responses: tuple[tuple[str, str], ...] = ()
    schema_version: int = 3

    def complete_activity(
        self,
        activity_id: str,
        *,
        required_activity_ids: tuple[str, ...],
        required_checkpoint_ids: tuple[str, ...],
        required_section_ids: tuple[str, ...] = (),
    ) -> PathwayProgress:
        completed = tuple(dict.fromkeys((*self.completed_activity_ids, activity_id)))
        return self._with_completion(
            completed,
            self.completed_checkpoint_ids,
            required_activity_ids,
            required_checkpoint_ids,
            required_section_ids,
        )

    def save_activity_response(
        self,
        activity_id: str,
        response: str,
        *,
        required_activity_ids: tuple[str, ...],
        required_checkpoint_ids: tuple[str, ...],
        required_section_ids: tuple[str, ...] = (),
    ) -> PathwayProgress:
        """Record reasoning evidence before completing an evidence-bearing activity."""

        text = response.strip()
        if not text:
            raise ValueError("Activity evidence cannot be blank.")
        responses = dict(self.activity_responses)
        responses[activity_id] = text
        return replace(self, activity_responses=tuple(responses.items())).complete_activity(
            activity_id,
            required_activity_ids=required_activity_ids,
            required_checkpoint_ids=required_checkpoint_ids,
            required_section_ids=required_section_ids,
        )

    def complete_checkpoint(
        self,
        checkpoint_id: str,
        *,
        required_activity_ids: tuple[str, ...],
        required_checkpoint_ids: tuple[str, ...],
        required_section_ids: tuple[str, ...] = (),
        objective_ids: tuple[str, ...] = (),
        attempt_id: str | None = None,
    ) -> PathwayProgress:
        completed = tuple(dict.fromkeys((*self.completed_checkpoint_ids, checkpoint_id)))
        updated = self._with_completion(
            self.completed_activity_ids,
            completed,
            required_activity_ids,
            required_checkpoint_ids,
            required_section_ids,
        )
        return replace(
            updated,
            assessment_attempt_ids=tuple(
                dict.fromkeys(
                    (*self.assessment_attempt_ids, *((attempt_id,) if attempt_id else ()))
                )
            ),
        )

    def save_prediction(
        self,
        response: str,
        prediction_activity_id: str,
        *,
        required_activity_ids: tuple[str, ...],
        required_checkpoint_ids: tuple[str, ...],
        required_section_ids: tuple[str, ...] = (),
    ) -> PathwayProgress:
        text = response.strip()
        if not text:
            raise ValueError("Prediction cannot be blank.")
        progress = replace(self, prediction=text)
        return progress.complete_activity(
            prediction_activity_id,
            required_activity_ids=required_activity_ids,
            required_checkpoint_ids=required_checkpoint_ids,
            required_section_ids=required_section_ids,
        )

    def reset_prediction(self, prediction_activity_id: str) -> PathwayProgress:
        return replace(
            self,
            prediction=None,
            completed_activity_ids=tuple(
                item for item in self.completed_activity_ids if item != prediction_activity_id
            ),
            completed=False,
        )

    def save_reflection(
        self,
        response: str,
        reflection_activity_id: str,
        *,
        required_activity_ids: tuple[str, ...],
        required_checkpoint_ids: tuple[str, ...],
        required_section_ids: tuple[str, ...] = (),
    ) -> PathwayProgress:
        text = response.strip()
        if not text:
            raise ValueError("Reflection cannot be blank.")
        progress = replace(self, reflection=text)
        return progress.complete_activity(
            reflection_activity_id,
            required_activity_ids=required_activity_ids,
            required_checkpoint_ids=required_checkpoint_ids,
            required_section_ids=required_section_ids,
        )

    def complete_section(
        self,
        section_id: str,
        *,
        required_activity_ids: tuple[str, ...],
        required_checkpoint_ids: tuple[str, ...],
        required_section_ids: tuple[str, ...],
        next_section_id: str | None = None,
    ) -> PathwayProgress:
        sections = tuple(dict.fromkeys((*self.completed_section_ids, section_id)))
        finished = (
            set(required_activity_ids) <= set(self.completed_activity_ids)
            and set(required_checkpoint_ids) <= set(self.completed_checkpoint_ids)
            and set(required_section_ids) <= set(sections)
        )
        return replace(
            self,
            completed_section_ids=sections,
            last_section_id=next_section_id or section_id,
            completed=finished,
        )

    def _with_completion(
        self,
        activity_ids: tuple[str, ...],
        checkpoint_ids: tuple[str, ...],
        required_activity_ids: tuple[str, ...],
        required_checkpoint_ids: tuple[str, ...],
        required_section_ids: tuple[str, ...] = (),
    ) -> PathwayProgress:
        finished = (
            set(required_activity_ids) <= set(activity_ids)
            and set(required_checkpoint_ids) <= set(checkpoint_ids)
            and set(required_section_ids) <= set(self.completed_section_ids)
        )
        return replace(
            self,
            completed_activity_ids=activity_ids,
            completed_checkpoint_ids=checkpoint_ids,
            completed=finished,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "lesson_id": self.lesson_id,
            "completed_activity_ids": list(self.completed_activity_ids),
            "completed_checkpoint_ids": list(self.completed_checkpoint_ids),
            "prediction": self.prediction,
            "reflection": self.reflection,
            "completed": self.completed,
            "mastered_objective_ids": list(self.mastered_objective_ids),
            "assessment_attempt_ids": list(self.assessment_attempt_ids),
            "completed_section_ids": list(self.completed_section_ids),
            "last_section_id": self.last_section_id,
            "activity_responses": [list(item) for item in self.activity_responses],
        }

    @classmethod
    def from_dict(cls, data: object, *, lesson_id: str) -> PathwayProgress:
        if not isinstance(data, dict):
            return cls(lesson_id)
        schema_version = int(data.get("schema_version", 1))
        if schema_version not in {1, 2, 3}:
            raise ValueError(f"Unsupported pathway-progress schema {schema_version}.")
        return cls(
            lesson_id=lesson_id,
            completed_activity_ids=tuple(
                str(item) for item in data.get("completed_activity_ids", ())
            ),
            completed_checkpoint_ids=tuple(
                str(item) for item in data.get("completed_checkpoint_ids", ())
            ),
            prediction=str(data["prediction"]) if data.get("prediction") else None,
            reflection=str(data["reflection"]) if data.get("reflection") else None,
            completed=bool(data.get("completed", False)),
            mastered_objective_ids=tuple(
                str(item) for item in data.get("mastered_objective_ids", ())
            ),
            assessment_attempt_ids=tuple(
                str(item) for item in data.get("assessment_attempt_ids", ())
            ),
            completed_section_ids=tuple(
                str(item) for item in data.get("completed_section_ids", ())
            ),
            last_section_id=str(data["last_section_id"]) if data.get("last_section_id") else None,
            activity_responses=tuple(
                (str(item[0]), str(item[1]))
                for item in data.get("activity_responses", ())
                if isinstance(item, list | tuple) and len(item) == 2
            ),
        )


def prerequisites_satisfied(
    lesson: Lesson, progress_by_lesson: Mapping[str, PathwayProgress]
) -> bool:
    """Return whether every required lesson prerequisite has recorded mastery."""

    return all(
        not prerequisite.required
        or prerequisite.kind is not PrerequisiteKind.LESSON
        or (
            prerequisite.reference_id in progress_by_lesson
            and progress_by_lesson[prerequisite.reference_id].completed
        )
        for prerequisite in lesson.prerequisites
    )
