"""Shared simulation contracts for Physics Playground.

The contracts in this module deliberately contain no Streamlit dependencies.
Physics models can therefore be tested, serialized, reused in notebooks, or
driven by a future web component without importing the application UI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Generic, Mapping, Protocol, Sequence, TypeVar, runtime_checkable

from physics_playground.models.simulations import SimulationDefinition

JsonValue = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]


class EventKind(StrEnum):
    """Broad event categories shared by all simulations."""

    START = "start"
    MILESTONE = "milestone"
    COLLISION = "collision"
    TURNING_POINT = "turning_point"
    COMPLETION = "completion"
    WARNING = "warning"


class PlotKind(StrEnum):
    LINE = "line"
    SCATTER = "scatter"
    PHASE = "phase"
    BAR = "bar"
    HEATMAP = "heatmap"
    VECTOR_FIELD = "vector_field"


class AnimationKind(StrEnum):
    ONE_DIMENSIONAL = "one_dimensional"
    TWO_DIMENSIONAL = "two_dimensional"
    FIELD = "field"
    WAVE = "wave"


@runtime_checkable
class ParameterSet(Protocol):
    """Serializable, self-validating input accepted by a simulation."""

    def validate(self) -> None:
        """Raise ``PhysicsValidationError`` when the input is invalid."""

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible representation."""


@dataclass(frozen=True, slots=True)
class SummaryMetric:
    """One result value suitable for kid mode, expert mode, and JSON."""

    id: str
    label: str
    value: float
    unit: str = ""
    display_value: str | None = None
    comparison: str | None = None


@dataclass(frozen=True, slots=True)
class SimulationEvent:
    """A meaningful occurrence detected by the physics model."""

    id: str
    kind: EventKind
    time_s: float
    label: str
    details: Mapping[str, JsonValue] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PlotSeries:
    """A named series displayed on one analytical plot."""

    id: str
    label: str
    x: tuple[float, ...]
    y: tuple[float, ...]
    color: str | None = None


@dataclass(frozen=True, slots=True)
class PlotData:
    """Renderer-neutral analytical graph data."""

    id: str
    title: str
    x_label: str
    y_label: str
    series: tuple[PlotSeries, ...]
    kind: PlotKind = PlotKind.LINE


@dataclass(frozen=True, slots=True)
class AnimationTrack:
    """One animated object's sampled coordinates and optional style."""

    id: str
    label: str
    x: tuple[float, ...]
    y: tuple[float, ...] | None = None
    style: Mapping[str, JsonValue] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AnimationData:
    """Renderer-neutral trajectory data consumed by canvas code."""

    kind: AnimationKind
    time_s: tuple[float, ...]
    tracks: tuple[AnimationTrack, ...]
    duration_ms: int
    view: Mapping[str, float] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ModelAssumption:
    id: str
    statement: str
    consequence: str | None = None


@dataclass(frozen=True, slots=True)
class MissionEvaluation:
    mission_id: str
    completed: bool
    reason: str
    evidence: Mapping[str, JsonValue] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    """Difference between two compatible trials."""

    baseline_trial_id: str
    comparison_trial_id: str
    metric_deltas: Mapping[str, float]


P = TypeVar("P", bound=ParameterSet)


@dataclass(frozen=True, slots=True)
class ContractResult(Generic[P]):
    """Complete output of a simulation run.

    ``parameters`` is retained with the output so a trial is reproducible.
    Plot and animation payloads are optional because some simulations may be
    analytical-only or intentionally text-first.
    """

    simulation_id: str
    parameters: P
    metrics: tuple[SummaryMetric, ...]
    events: tuple[SimulationEvent, ...] = ()
    plots: tuple[PlotData, ...] = ()
    animation: AnimationData | None = None
    assumptions: tuple[ModelAssumption, ...] = ()
    missions: tuple[MissionEvaluation, ...] = ()
    completed: bool = True
    warnings: tuple[str, ...] = ()
    outcome_description: str = ""
    model_version: str = "unknown"
    random_seed: int = 0

    def metric(self, metric_id: str) -> SummaryMetric:
        for metric in self.metrics:
            if metric.id == metric_id:
                return metric
        raise KeyError(f"Unknown metric: {metric_id}")


@runtime_checkable
class MissionEvaluator(Protocol[P]):
    def evaluate(self, result: ContractResult[P]) -> Sequence[MissionEvaluation]:
        """Evaluate missions without mutating Streamlit session state."""


@runtime_checkable
class Simulation(Protocol[P]):
    """Common interface implemented by every migrated simulation."""

    metadata: SimulationDefinition

    def run(self, parameters: P) -> ContractResult[P]:
        """Run a deterministic, pure-Python simulation."""

    def compare(
        self,
        baseline: ContractResult[P],
        comparison: ContractResult[P],
    ) -> ComparisonResult:
        """Compare shared summary metrics from two trials."""


def shared_metric_deltas(
    baseline: ContractResult[Any],
    comparison: ContractResult[Any],
) -> dict[str, float]:
    """Return comparison minus baseline for metrics present in both results."""

    baseline_metrics = {metric.id: metric.value for metric in baseline.metrics}
    return {
        metric.id: metric.value - baseline_metrics[metric.id]
        for metric in comparison.metrics
        if metric.id in baseline_metrics
    }
