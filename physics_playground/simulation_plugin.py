"""Framework-neutral contract for enrolling a simulation in the shared runtime."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from physics_playground.contracts import ContractResult, JsonValue, ParameterSet
from physics_playground.models.expansion import PresentationCapability
from physics_playground.models.simulations import SimulationDefinition

P = TypeVar("P", bound=ParameterSet)
R = TypeVar("R", bound=ContractResult[Any])

ModelRunner = Callable[[P], R]
NotebookParameterSerializer = Callable[[P], dict[str, JsonValue]]
AccessibleSummary = Callable[[R], str]


@dataclass(frozen=True, slots=True)
class CapabilityImplementation:
    """One capability and the importable presentation function that implements it."""

    capability: PresentationCapability
    entrypoint: str


@dataclass(frozen=True, slots=True)
class PresentationAdapter:
    """Importable current-page and renderer seams, without importing either framework."""

    page_entrypoint: str
    renderer_entrypoint: str


@dataclass(frozen=True, slots=True)
class SimulationPlugin(Generic[P, R]):
    """Typed, immutable description of one simulation runtime integration.

    Identity and model version are intentionally derived from ``metadata`` so the
    plugin cannot disagree with the existing registry during staged migration.
    """

    metadata: SimulationDefinition
    parameter_type: type[P]
    result_type: type[R]
    model_runner: ModelRunner[P, R]
    presentation: PresentationAdapter
    capability_implementations: tuple[CapabilityImplementation, ...]
    serialize_notebook_parameters: NotebookParameterSerializer[P]
    accessible_summary: AccessibleSummary[R]

    @property
    def id(self) -> str:
        """Return the stable registry identity."""

        return self.metadata.id

    @property
    def model_version(self) -> str:
        """Return the single model version owned by registry metadata."""

        return self.metadata.model_version

    @property
    def supported_capabilities(self) -> frozenset[PresentationCapability]:
        """Return capabilities with declared presentation implementations."""

        return frozenset(item.capability for item in self.capability_implementations)


def serialize_parameter_set(parameters: P) -> dict[str, JsonValue]:
    """Use the established parameter contract for notebook serialization."""

    return parameters.to_dict()


def contract_accessible_summary(result: ContractResult[Any]) -> str:
    """Use the model-authored nonvisual outcome as the default accessible summary."""

    return result.outcome_description
