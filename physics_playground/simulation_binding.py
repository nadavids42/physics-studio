"""Typed bridge between reusable content, presets, and simulation models."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Generic, TypeVar, cast

from physics_playground.contract_validation import validate_contract_result
from physics_playground.contracts import ContractResult, JsonValue, ParameterSet, SummaryMetric
from physics_playground.model_metadata import ModelMetadata
from physics_playground.serialization import dataclass_from_dict, to_jsonable
from physics_playground.validation import PhysicsValidationError

P = TypeVar("P", bound=ParameterSet)
R = TypeVar("R", bound=ContractResult[Any])


@dataclass(frozen=True, slots=True)
class MetricDefinition:
    id: str
    label: str
    unit: str = ""


@dataclass(frozen=True, slots=True)
class ExpectedMetric:
    metric_id: str
    value: float
    absolute_tolerance: float = 1e-9
    relative_tolerance: float = 1e-9

    def matches(self, actual: float) -> bool:
        return math.isclose(
            actual,
            self.value,
            abs_tol=self.absolute_tolerance,
            rel_tol=self.relative_tolerance,
        )


@dataclass(frozen=True, slots=True)
class SimulationPreset:
    """Versioned, serializable setup that can be handed to a simulation."""

    id: str
    simulation_id: str
    title: str
    parameters: Mapping[str, JsonValue]
    model_version: str
    expected_metrics: tuple[ExpectedMetric, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "parameters", MappingProxyType(dict(self.parameters)))
        if not all((self.id, self.simulation_id, self.title, self.model_version)):
            raise ValueError("Simulation presets require IDs, a title, and a model version.")
        metric_ids = [item.metric_id for item in self.expected_metrics]
        if len(metric_ids) != len(set(metric_ids)):
            raise ValueError("Expected preset metrics must have unique IDs.")
        if any(
            item.absolute_tolerance < 0 or item.relative_tolerance < 0
            for item in self.expected_metrics
        ):
            raise ValueError("Expected metric tolerances cannot be negative.")

    def to_dict(self) -> dict[str, JsonValue]:
        return cast(dict[str, JsonValue], to_jsonable(self))

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> SimulationPreset:
        expected_payload = payload.get("expected_metrics", ())
        if not isinstance(expected_payload, list | tuple):
            raise TypeError("Expected metrics must be a list or tuple.")
        expected = tuple(
            ExpectedMetric(**dict(cast(Mapping[str, Any], item))) for item in expected_payload
        )
        parameters_payload = payload.get("parameters")
        if not isinstance(parameters_payload, Mapping):
            raise TypeError("Preset parameters must be a mapping.")
        return cls(
            id=str(payload["id"]),
            simulation_id=str(payload["simulation_id"]),
            title=str(payload["title"]),
            parameters=cast(dict[str, JsonValue], dict(parameters_payload)),
            model_version=str(payload["model_version"]),
            expected_metrics=expected,
        )


@dataclass(frozen=True, slots=True)
class SimulationBinding(Generic[P, R]):
    """Runtime contract used by lessons, presets, and direct simulator tools."""

    simulation_id: str
    parameter_model: type[P]
    result_model: type[R]
    model_version: str
    runner: Callable[[P], R]
    metadata: ModelMetadata
    metrics: tuple[MetricDefinition, ...]

    def __post_init__(self) -> None:
        if self.metadata.simulation_id != self.simulation_id:
            raise ValueError("Binding and metadata simulation IDs must match.")
        if not self.model_version:
            raise ValueError("A simulation binding requires a model version.")
        metric_ids = [item.id for item in self.metrics]
        if not metric_ids or len(metric_ids) != len(set(metric_ids)):
            raise ValueError("Binding metrics must be non-empty and uniquely identified.")
        self.metadata.validate()

    def parameters_from_dict(self, payload: Mapping[str, JsonValue]) -> P:
        parameters = dataclass_from_dict(self.parameter_model, dict(payload))
        parameters.validate()
        return parameters

    def run(self, parameters: P | Mapping[str, JsonValue]) -> R:
        typed = (
            self.parameters_from_dict(parameters) if isinstance(parameters, Mapping) else parameters
        )
        typed.validate()
        result = self.runner(typed)
        if not isinstance(result, self.result_model):
            raise PhysicsValidationError(f"{self.simulation_id} returned the wrong result model.")
        validate_contract_result(result)
        if result.simulation_id != self.simulation_id:
            raise PhysicsValidationError("Result and binding simulation IDs do not match.")
        if result.model_version != self.model_version:
            raise PhysicsValidationError("Result and binding model versions do not match.")
        declared = {item.id: item for item in self.metrics}
        for metric in result.metrics:
            definition = declared.get(metric.id)
            if definition is None:
                raise PhysicsValidationError(f"Result contains undeclared metric {metric.id!r}.")
            if metric.unit != definition.unit:
                raise PhysicsValidationError(f"Metric {metric.id!r} has an inconsistent unit.")
        return result

    def run_preset(self, preset: SimulationPreset, *, check_expected: bool = True) -> R:
        if preset.simulation_id != self.simulation_id:
            raise PhysicsValidationError("Preset and binding simulation IDs do not match.")
        if preset.model_version != self.model_version:
            raise PhysicsValidationError("Preset and binding model versions do not match.")
        result = self.run(preset.parameters)
        if check_expected:
            self.validate_expected_metrics(preset, result)
        return result

    def validate_expected_metrics(self, preset: SimulationPreset, result: R) -> None:
        for expected in preset.expected_metrics:
            try:
                actual = result.metric(expected.metric_id).value
            except KeyError as error:
                raise PhysicsValidationError(
                    f"Preset expects unknown metric {expected.metric_id!r}."
                ) from error
            if not expected.matches(actual):
                raise PhysicsValidationError(
                    f"Metric {expected.metric_id!r} was {actual:g}; expected {expected.value:g}."
                )

    def metric(self, result: R, metric_id: str) -> SummaryMetric:
        if metric_id not in {item.id for item in self.metrics}:
            raise KeyError(f"Unknown binding metric: {metric_id}")
        return result.metric(metric_id)
