"""Minimal constant-gravity example implementing the complete contract.

This example is intentionally not registered as an eighth playground page. It
exists to show how each legacy simulation can be migrated incrementally.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace

import numpy as np

from physics_playground.contracts import (
    AnimationData,
    AnimationKind,
    AnimationTrack,
    ComparisonResult,
    ContractResult,
    EventKind,
    MissionEvaluation,
    ModelAssumption,
    PlotData,
    PlotSeries,
    SimulationEvent,
    SummaryMetric,
    shared_metric_deltas,
)
from physics_playground.models.simulations import SimulationDefinition, SimulationMode
from physics_playground.serialization import to_jsonable
from physics_playground.validation import require_positive


@dataclass(frozen=True, slots=True)
class FreeFallParameters:
    height_m: float = 20.0
    gravity_m_s2: float = 9.81
    samples: int = 120

    def validate(self) -> None:
        require_positive("height_m", self.height_m)
        require_positive("gravity_m_s2", self.gravity_m_s2)
        if self.samples < 2:
            raise ValueError("samples must be at least 2.")

    def to_dict(self) -> dict[str, object]:
        return to_jsonable(asdict(self))


class FreeFallMissionEvaluator:
    def evaluate(
        self,
        result: ContractResult[FreeFallParameters],
    ) -> tuple[MissionEvaluation, ...]:
        impact_speed = result.metric("impact_speed").value
        return (
            MissionEvaluation(
                mission_id="example_fast_fall",
                completed=impact_speed >= 20.0,
                reason="Reach an impact speed of at least 20 m/s.",
                evidence={"impact_speed_m_s": impact_speed},
            ),
        )


class FreeFallSimulation:
    metadata = SimulationDefinition(
        id="free_fall_example",
        title="Free-Fall Contract Example",
        icon="⬇️",
        description="A minimal constant-gravity contract implementation",
        page_module="",
        mission_group="Contract Examples",
        modes=(SimulationMode.KID, SimulationMode.EXPERT),
    )

    def __init__(self) -> None:
        self._missions = FreeFallMissionEvaluator()

    def run(self, parameters: FreeFallParameters) -> ContractResult[FreeFallParameters]:
        parameters.validate()
        flight_time = float(np.sqrt(2.0 * parameters.height_m / parameters.gravity_m_s2))
        time_s = np.linspace(0.0, flight_time, parameters.samples)
        height_m = parameters.height_m - 0.5 * parameters.gravity_m_s2 * time_s**2
        speed_m_s = parameters.gravity_m_s2 * time_s
        height_m[-1] = 0.0

        result = ContractResult(
            simulation_id=self.metadata.id,
            parameters=parameters,
            metrics=(
                SummaryMetric("flight_time", "Time to ground", flight_time, "s", f"{flight_time:.2f} s"),
                SummaryMetric("impact_speed", "Impact speed", float(speed_m_s[-1]), "m/s", f"{speed_m_s[-1]:.1f} m/s"),
            ),
            events=(
                SimulationEvent("release", EventKind.START, 0.0, "Object released"),
                SimulationEvent("impact", EventKind.COMPLETION, flight_time, "Object reaches the ground"),
            ),
            plots=(
                PlotData(
                    id="height_time",
                    title="Height over time",
                    x_label="Time (s)",
                    y_label="Height (m)",
                    series=(PlotSeries("height", "Height", tuple(time_s), tuple(height_m)),),
                ),
                PlotData(
                    id="speed_time",
                    title="Speed over time",
                    x_label="Time (s)",
                    y_label="Speed (m/s)",
                    series=(PlotSeries("speed", "Speed", tuple(time_s), tuple(speed_m_s)),),
                ),
            ),
            animation=AnimationData(
                kind=AnimationKind.ONE_DIMENSIONAL,
                time_s=tuple(time_s),
                tracks=(AnimationTrack("object", "Falling object", tuple(height_m)),),
                duration_ms=3_000,
                view={"minimum": 0.0, "maximum": parameters.height_m},
            ),
            assumptions=(
                ModelAssumption("constant_gravity", "Gravity is constant throughout the fall."),
                ModelAssumption("no_drag", "Air resistance is ignored.", "Real objects may fall more slowly."),
            ),
        )
        return replace(result, missions=self._missions.evaluate(result))

    def compare(
        self,
        baseline: ContractResult[FreeFallParameters],
        comparison: ContractResult[FreeFallParameters],
    ) -> ComparisonResult:
        if baseline.simulation_id != self.metadata.id or comparison.simulation_id != self.metadata.id:
            raise ValueError("Both results must come from the free-fall example.")
        return ComparisonResult("baseline", "comparison", shared_metric_deltas(baseline, comparison))
