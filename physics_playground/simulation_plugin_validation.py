"""Validation gates for framework-neutral simulation plugins."""

from __future__ import annotations

import inspect
import json
import re
from collections.abc import Iterable
from importlib import import_module
from typing import Any, get_type_hints

from physics_playground.contract_validation import validate_contract_result
from physics_playground.contracts import ContractResult, ParameterSet
from physics_playground.models.expansion import REQUIRED_MODE_REQUIREMENTS
from physics_playground.simulation_plugin import SimulationPlugin
from physics_playground.validation import PhysicsValidationError

MODEL_VERSION_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*-[0-9]+\.[0-9]+$")


def _resolve_callable(entrypoint: str, *, label: str) -> None:
    if not entrypoint or "." not in entrypoint:
        raise PhysicsValidationError(f"{label} must be a fully qualified entrypoint.")
    module_name, attribute = entrypoint.rsplit(".", 1)
    try:
        value = getattr(import_module(module_name), attribute)
    except (ImportError, AttributeError) as error:
        raise PhysicsValidationError(f"{label} is unavailable: {entrypoint}") from error
    if not callable(value):
        raise PhysicsValidationError(f"{label} must resolve to a callable: {entrypoint}")


def _validate_runner_annotations(plugin: SimulationPlugin[Any, Any]) -> None:
    signature = inspect.signature(plugin.model_runner)
    parameters = tuple(signature.parameters.values())
    if len(parameters) != 1:
        raise PhysicsValidationError("A plugin model runner must accept exactly one parameter.")
    try:
        hints = get_type_hints(plugin.model_runner)
    except (NameError, TypeError) as error:
        raise PhysicsValidationError(
            "A plugin model runner must have resolvable type hints."
        ) from error
    parameter_hint = hints.get(parameters[0].name)
    if parameter_hint is not plugin.parameter_type:
        raise PhysicsValidationError(
            "The model runner parameter annotation must match parameter_type."
        )
    if hints.get("return") is not plugin.result_type:
        raise PhysicsValidationError("The model runner return annotation must match result_type.")


def _validate_capabilities(plugin: SimulationPlugin[Any, Any]) -> None:
    implementations = plugin.capability_implementations
    capabilities = [item.capability for item in implementations]
    if not capabilities:
        raise PhysicsValidationError("A simulation plugin must implement at least one capability.")
    if len(capabilities) != len(set(capabilities)):
        raise PhysicsValidationError("Capability implementations must be unique.")
    required = {
        capability
        for requirement in REQUIRED_MODE_REQUIREMENTS
        if requirement.mode in plugin.metadata.modes
        for capability in requirement.capabilities
    }
    missing = required - set(capabilities)
    if missing:
        names = ", ".join(sorted(capability.value for capability in missing))
        raise PhysicsValidationError(f"Required capabilities lack implementations: {names}.")
    for implementation in implementations:
        _resolve_callable(
            implementation.entrypoint,
            label=f"{implementation.capability.value} capability implementation",
        )


def validate_simulation_plugin(plugin: SimulationPlugin[Any, Any]) -> None:
    """Validate one plugin against its declared types and a default model run."""

    if not plugin.id or plugin.id != plugin.metadata.id:
        raise PhysicsValidationError("A simulation plugin requires a stable metadata ID.")
    if not MODEL_VERSION_PATTERN.fullmatch(plugin.model_version):
        raise PhysicsValidationError(
            "model_version must use a stable '<model-name>-<major>.<minor>' form."
        )
    if not isinstance(plugin.parameter_type, type) or not issubclass(
        plugin.parameter_type, ParameterSet
    ):
        raise PhysicsValidationError("parameter_type must implement ParameterSet.")
    if not isinstance(plugin.result_type, type) or not issubclass(
        plugin.result_type, ContractResult
    ):
        raise PhysicsValidationError("result_type must extend ContractResult.")

    _validate_runner_annotations(plugin)
    _validate_capabilities(plugin)
    _resolve_callable(plugin.presentation.page_entrypoint, label="Page adapter")
    _resolve_callable(plugin.presentation.renderer_entrypoint, label="Renderer")

    try:
        parameters = plugin.parameter_type()
    except TypeError as error:
        raise PhysicsValidationError(
            "parameter_type must provide a default setup for enrollment validation."
        ) from error
    parameters.validate()
    payload = plugin.serialize_notebook_parameters(parameters)
    if not isinstance(payload, dict) or any(not isinstance(key, str) for key in payload):
        raise PhysicsValidationError("Notebook parameters must serialize to a string-keyed object.")
    try:
        json.dumps(payload, allow_nan=False, sort_keys=True)
    except (TypeError, ValueError) as error:
        raise PhysicsValidationError("Notebook parameters must be strict JSON values.") from error

    result = plugin.model_runner(parameters)
    if not isinstance(result, plugin.result_type):
        raise PhysicsValidationError("The model runner returned the wrong result type.")
    if not isinstance(result.parameters, plugin.parameter_type):
        raise PhysicsValidationError("The result contains the wrong parameter type.")
    if result.simulation_id != plugin.id:
        raise PhysicsValidationError("The result simulation ID does not match the plugin ID.")
    if result.model_version != plugin.model_version:
        raise PhysicsValidationError("The result model version does not match plugin metadata.")
    validate_contract_result(result)

    first_summary = plugin.accessible_summary(result)
    second_summary = plugin.accessible_summary(result)
    if not isinstance(first_summary, str) or not first_summary.strip():
        raise PhysicsValidationError("The accessible summary must be non-empty text.")
    if first_summary != second_summary:
        raise PhysicsValidationError("The accessible summary must be stable for the same result.")


def validate_simulation_plugins(plugins: Iterable[SimulationPlugin[Any, Any]]) -> None:
    """Validate a catalog and reject duplicate stable IDs."""

    values = tuple(plugins)
    ids = [plugin.id for plugin in values]
    if len(ids) != len(set(ids)):
        raise PhysicsValidationError("Simulation plugin IDs must be unique.")
    for plugin in values:
        validate_simulation_plugin(plugin)
