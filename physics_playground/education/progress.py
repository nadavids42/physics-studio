"""Pure progress operations for lesson pathways."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any


@dataclass(frozen=True, slots=True)
class PathwayProgress:
    lesson_id: str
    completed_activity_ids: tuple[str, ...] = ()
    completed_checkpoint_ids: tuple[str, ...] = ()
    prediction: str | None = None
    reflection: str | None = None
    completed: bool = False

    def complete_activity(
        self,
        activity_id: str,
        *,
        required_activity_ids: tuple[str, ...],
        required_checkpoint_ids: tuple[str, ...],
    ) -> PathwayProgress:
        completed = tuple(dict.fromkeys((*self.completed_activity_ids, activity_id)))
        return self._with_completion(
            completed, self.completed_checkpoint_ids, required_activity_ids, required_checkpoint_ids
        )

    def complete_checkpoint(
        self,
        checkpoint_id: str,
        *,
        required_activity_ids: tuple[str, ...],
        required_checkpoint_ids: tuple[str, ...],
    ) -> PathwayProgress:
        completed = tuple(dict.fromkeys((*self.completed_checkpoint_ids, checkpoint_id)))
        return self._with_completion(
            self.completed_activity_ids, completed, required_activity_ids, required_checkpoint_ids
        )

    def save_prediction(
        self,
        response: str,
        prediction_activity_id: str,
        *,
        required_activity_ids: tuple[str, ...],
        required_checkpoint_ids: tuple[str, ...],
    ) -> PathwayProgress:
        text = response.strip()
        if not text:
            raise ValueError("Prediction cannot be blank.")
        progress = replace(self, prediction=text)
        return progress.complete_activity(
            prediction_activity_id,
            required_activity_ids=required_activity_ids,
            required_checkpoint_ids=required_checkpoint_ids,
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
    ) -> PathwayProgress:
        text = response.strip()
        if not text:
            raise ValueError("Reflection cannot be blank.")
        progress = replace(self, reflection=text)
        return progress.complete_activity(
            reflection_activity_id,
            required_activity_ids=required_activity_ids,
            required_checkpoint_ids=required_checkpoint_ids,
        )

    def _with_completion(
        self,
        activity_ids: tuple[str, ...],
        checkpoint_ids: tuple[str, ...],
        required_activity_ids: tuple[str, ...],
        required_checkpoint_ids: tuple[str, ...],
    ) -> PathwayProgress:
        finished = set(required_activity_ids) <= set(activity_ids) and set(
            required_checkpoint_ids
        ) <= set(checkpoint_ids)
        return replace(
            self,
            completed_activity_ids=activity_ids,
            completed_checkpoint_ids=checkpoint_ids,
            completed=finished,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "lesson_id": self.lesson_id,
            "completed_activity_ids": list(self.completed_activity_ids),
            "completed_checkpoint_ids": list(self.completed_checkpoint_ids),
            "prediction": self.prediction,
            "reflection": self.reflection,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: object, *, lesson_id: str) -> PathwayProgress:
        if not isinstance(data, dict):
            return cls(lesson_id)
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
        )
