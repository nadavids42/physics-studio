"""Session-friendly experiment notebook models and operations.

The service itself has no Streamlit dependency. A UI stores one ``ExperimentNotebook``
instance in ``st.session_state`` and any migrated simulation can append trials.
"""

from __future__ import annotations

import csv
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from io import StringIO
from uuid import uuid4

from physics_playground.contracts import JsonValue
from physics_playground.performance import MAX_NOTEBOOK_TRIALS
from physics_playground.serialization import dumps


@dataclass(frozen=True, slots=True)
class TrialRecord:
    id: str
    simulation_id: str
    trial_number: int
    timestamp: str
    parameters: Mapping[str, JsonValue]
    prediction: str | None
    result_summary: str
    metrics: Mapping[str, float]
    earned_badges: tuple[str, ...]
    random_seed: int
    model_version: str
    learner_observation: str | None = None
    label: str | None = None

    @property
    def display_label(self) -> str:
        label = f" — {self.label}" if self.label else ""
        return f"#{self.trial_number} {self.simulation_id}{label}"


@dataclass(frozen=True, slots=True)
class TrialComparison:
    run_a: TrialRecord
    run_b: TrialRecord
    metric_deltas: Mapping[str, float]
    changed_parameters: Mapping[str, tuple[JsonValue, JsonValue]]


@dataclass(frozen=True, slots=True)
class LessonReflection:
    id: str
    lesson_id: str
    timestamp: str
    prompt: str
    response: str


@dataclass(slots=True)
class ExperimentNotebook:
    trials: list[TrialRecord] = field(default_factory=list)
    lesson_reflections: list[LessonReflection] = field(default_factory=list)
    pinned_run_a_id: str | None = None
    next_trial_number: int = 1

    def add_trial(
        self,
        *,
        simulation_id: str,
        parameters: Mapping[str, JsonValue],
        prediction: str | None,
        result_summary: str,
        metrics: Mapping[str, float],
        earned_badges: tuple[str, ...],
        random_seed: int,
        model_version: str,
        learner_observation: str | None = None,
        label: str | None = None,
    ) -> TrialRecord:
        trial = TrialRecord(
            id=uuid4().hex,
            simulation_id=simulation_id,
            trial_number=self.next_trial_number,
            timestamp=datetime.now(UTC).isoformat(),
            parameters=dict(parameters),
            prediction=prediction,
            result_summary=result_summary,
            metrics=dict(metrics),
            earned_badges=tuple(earned_badges),
            random_seed=random_seed,
            model_version=model_version,
            learner_observation=learner_observation.strip()
            if learner_observation and learner_observation.strip()
            else None,
            label=label,
        )
        self.trials.append(trial)
        if len(self.trials) > MAX_NOTEBOOK_TRIALS:
            removed = self.trials.pop(0)
            if self.pinned_run_a_id == removed.id:
                self.pinned_run_a_id = None
        self.next_trial_number += 1
        return trial

    def save_lesson_reflection(
        self, *, lesson_id: str, prompt: str, response: str
    ) -> LessonReflection:
        text = response.strip()
        if not text:
            raise ValueError("Lesson reflection cannot be blank.")
        reflection = LessonReflection(
            id=uuid4().hex,
            lesson_id=lesson_id,
            timestamp=datetime.now(UTC).isoformat(),
            prompt=prompt,
            response=text,
        )
        self.lesson_reflections = [
            item for item in self.lesson_reflections if item.lesson_id != lesson_id
        ]
        self.lesson_reflections.append(reflection)
        return reflection

    def filtered(self, simulation_id: str | None = None) -> list[TrialRecord]:
        if not simulation_id:
            return list(self.trials)
        return [trial for trial in self.trials if trial.simulation_id == simulation_id]

    def get(self, trial_id: str) -> TrialRecord:
        for trial in self.trials:
            if trial.id == trial_id:
                return trial
        raise KeyError(f"Unknown notebook trial: {trial_id}")

    def delete(self, trial_id: str) -> None:
        self.get(trial_id)
        self.trials = [trial for trial in self.trials if trial.id != trial_id]
        if self.pinned_run_a_id == trial_id:
            self.pinned_run_a_id = None

    def pin(self, trial_id: str) -> None:
        self.get(trial_id)
        self.pinned_run_a_id = trial_id

    def compare(self, run_a_id: str, run_b_id: str) -> TrialComparison:
        run_a, run_b = self.get(run_a_id), self.get(run_b_id)
        shared_metrics = run_a.metrics.keys() & run_b.metrics.keys()
        shared_parameters = run_a.parameters.keys() & run_b.parameters.keys()
        return TrialComparison(
            run_a,
            run_b,
            {key: run_b.metrics[key] - run_a.metrics[key] for key in shared_metrics},
            {
                key: (run_a.parameters[key], run_b.parameters[key])
                for key in shared_parameters
                if run_a.parameters[key] != run_b.parameters[key]
            },
        )

    def reset(self) -> None:
        self.trials.clear()
        self.lesson_reflections.clear()
        self.pinned_run_a_id = None
        self.next_trial_number = 1

    def to_json(self, *, indent: int = 2) -> str:
        return dumps(self, indent=indent)

    def to_csv(self) -> str:
        parameter_names = sorted({key for trial in self.trials for key in trial.parameters})
        metric_names = sorted({key for trial in self.trials for key in trial.metrics})
        fields = [
            "trial_number",
            "simulation_id",
            "timestamp",
            "prediction",
            "result_summary",
            "earned_badges",
            "random_seed",
            "model_version",
            "learner_observation",
            "label",
        ]
        fields += [f"parameter.{name}" for name in parameter_names]
        fields += [f"metric.{name}" for name in metric_names]
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for trial in self.trials:
            row = {
                "trial_number": trial.trial_number,
                "simulation_id": trial.simulation_id,
                "timestamp": trial.timestamp,
                "prediction": trial.prediction or "",
                "result_summary": trial.result_summary,
                "earned_badges": ";".join(trial.earned_badges),
                "random_seed": trial.random_seed,
                "model_version": trial.model_version,
                "learner_observation": trial.learner_observation or "",
                "label": trial.label or "",
            }
            row.update(
                {f"parameter.{name}": trial.parameters.get(name, "") for name in parameter_names}
            )
            row.update({f"metric.{name}": trial.metrics.get(name, "") for name in metric_names})
            writer.writerow(row)
        return output.getvalue()

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> ExperimentNotebook:
        raw_trials = payload.get("trials", [])
        if not isinstance(raw_trials, list):
            raise TypeError("Notebook trials must be a list.")
        trials = [
            TrialRecord(
                id=str(item["id"]),
                simulation_id=str(item["simulation_id"]),
                trial_number=int(item["trial_number"]),
                timestamp=str(item["timestamp"]),
                parameters=dict(item.get("parameters", {})),
                prediction=item.get("prediction"),
                result_summary=str(item.get("result_summary", "")),
                metrics={key: float(value) for key, value in item.get("metrics", {}).items()},
                earned_badges=tuple(item.get("earned_badges", ())),
                random_seed=int(item.get("random_seed", 0)),
                model_version=str(item.get("model_version", "unknown")),
                learner_observation=item.get("learner_observation"),
                label=item.get("label"),
            )
            for item in raw_trials
            if isinstance(item, Mapping)
        ]
        raw_reflections = payload.get("lesson_reflections", [])
        if not isinstance(raw_reflections, list):
            raise TypeError("Notebook lesson reflections must be a list.")
        reflections = [
            LessonReflection(
                id=str(item["id"]),
                lesson_id=str(item["lesson_id"]),
                timestamp=str(item["timestamp"]),
                prompt=str(item.get("prompt", "")),
                response=str(item.get("response", "")),
            )
            for item in raw_reflections
            if isinstance(item, Mapping)
        ]
        pinned = payload.get("pinned_run_a_id")
        if pinned is not None and not isinstance(pinned, str):
            raise TypeError("Pinned trial ID must be a string or null.")
        raw_next_trial = payload.get("next_trial_number", len(trials) + 1)
        if not isinstance(raw_next_trial, int | str | bytes | bytearray):
            raise TypeError("Next trial number must be integer-like.")
        return cls(
            trials=trials,
            lesson_reflections=reflections,
            pinned_run_a_id=pinned,
            next_trial_number=int(raw_next_trial),
        )
