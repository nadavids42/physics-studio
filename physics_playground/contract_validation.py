"""Cross-cutting validation for shared simulation contract objects."""

from __future__ import annotations

import math

from physics_playground.contracts import AnimationData, ContractResult, ParameterSet, PlotData
from physics_playground.validation import PhysicsValidationError


def _require_finite_sequence(label: str, values: tuple[float, ...]) -> None:
    if not values:
        raise PhysicsValidationError(f"{label} cannot be empty.")
    if not all(math.isfinite(value) for value in values):
        raise PhysicsValidationError(f"{label} contains non-finite values.")


def validate_plot(plot: PlotData) -> None:
    if not plot.series:
        raise PhysicsValidationError(f"Plot {plot.id!r} must contain at least one series.")
    for series in plot.series:
        _require_finite_sequence(f"Plot series {series.id!r} x-values", series.x)
        _require_finite_sequence(f"Plot series {series.id!r} y-values", series.y)
        if len(series.x) != len(series.y):
            raise PhysicsValidationError(f"Plot series {series.id!r} x/y lengths do not match.")


def validate_animation(animation: AnimationData) -> None:
    _require_finite_sequence("Animation time", animation.time_s)
    if animation.duration_ms <= 0:
        raise PhysicsValidationError("Animation duration must be greater than zero.")
    if any(later < earlier for earlier, later in zip(animation.time_s, animation.time_s[1:])):
        raise PhysicsValidationError("Animation time must be non-decreasing.")
    if not animation.tracks:
        raise PhysicsValidationError("Animation must contain at least one track.")
    for track in animation.tracks:
        _require_finite_sequence(f"Animation track {track.id!r} x-values", track.x)
        if len(track.x) != len(animation.time_s):
            raise PhysicsValidationError(f"Animation track {track.id!r} length does not match time.")
        if track.y is not None:
            _require_finite_sequence(f"Animation track {track.id!r} y-values", track.y)
            if len(track.y) != len(animation.time_s):
                raise PhysicsValidationError(f"Animation track {track.id!r} y length does not match time.")


def validate_contract_result(result: ContractResult[ParameterSet]) -> None:
    """Validate structural invariants shared by every simulation result."""

    result.parameters.validate()
    if not result.simulation_id:
        raise PhysicsValidationError("simulation_id cannot be empty.")
    if not result.model_version.strip():
        raise PhysicsValidationError("model_version cannot be empty.")
    if result.random_seed < 0:
        raise PhysicsValidationError("random_seed must be non-negative.")
    metric_ids = [metric.id for metric in result.metrics]
    if not metric_ids or len(metric_ids) != len(set(metric_ids)):
        raise PhysicsValidationError("Result metrics must be non-empty and uniquely identified.")
    if not all(math.isfinite(metric.value) for metric in result.metrics):
        raise PhysicsValidationError("Result metrics must be finite.")
    event_ids = [event.id for event in result.events]
    if len(event_ids) != len(set(event_ids)):
        raise PhysicsValidationError("Result events must be uniquely identified.")
    if not all(math.isfinite(event.time_s) and event.time_s >= 0 for event in result.events):
        raise PhysicsValidationError("Event times must be finite and non-negative.")
    for plot in result.plots:
        validate_plot(plot)
    if result.animation is not None:
        validate_animation(result.animation)
