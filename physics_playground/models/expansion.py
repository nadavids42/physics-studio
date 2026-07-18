"""Machine-checkable architecture for Physics Studio expansion simulations.

This module describes what a new simulation must provide without importing
Streamlit.  Subject packages can therefore implement and test physics first,
then attach presentation adapters without coupling the model to the UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import ClassVar, Generic, Protocol, TypeVar, runtime_checkable

from physics_playground.contracts import ContractResult, ModelAssumption, ParameterSet
from physics_playground.missions.models import MissionDefinition
from physics_playground.models.simulations import LearningMode, SimulationDefinition


class SubjectArea(StrEnum):
    MECHANICS = "mechanics"
    WAVES_AND_OSCILLATIONS = "waves_and_oscillations"
    LIGHT_AND_ELECTRICITY = "light_and_electricity"
    FLUIDS_AND_MATTER = "fluids_and_matter"


class PresentationCapability(StrEnum):
    PREDICTION = "prediction"
    BASELINE_COMPARISON = "baseline_comparison"
    ANALYTICAL_CHARTS = "analytical_charts"
    EQUATIONS = "equations"
    ASSUMPTIONS = "assumptions"
    LIMITATIONS = "limitations"
    ADVANCED_CONTROLS = "advanced_controls"


@dataclass(frozen=True, slots=True)
class ModeRequirements:
    """Required behavior for one learning mode."""

    mode: LearningMode
    capabilities: tuple[PresentationCapability, ...]


REQUIRED_MODE_REQUIREMENTS = (
    ModeRequirements(LearningMode.EXPLORE, (PresentationCapability.PREDICTION,)),
    ModeRequirements(LearningMode.COMPARE, (PresentationCapability.BASELINE_COMPARISON,)),
    ModeRequirements(LearningMode.ANALYZE, (PresentationCapability.ANALYTICAL_CHARTS,)),
    ModeRequirements(
        LearningMode.MODEL,
        (
            PresentationCapability.EQUATIONS,
            PresentationCapability.ASSUMPTIONS,
            PresentationCapability.LIMITATIONS,
        ),
    ),
)


@dataclass(frozen=True, slots=True)
class AccessibilityRequirements:
    outcome_text: bool = True
    keyboard_controls: bool = True
    reduced_motion: bool = True
    high_contrast: bool = True
    color_independent_charts: bool = True
    responsive_layout: bool = True
    accessible_chart_captions: bool = True


@dataclass(frozen=True, slots=True)
class TestRequirements:
    # Pytest otherwise mistakes this public architecture model for a test class.
    __test__: ClassVar[bool] = False

    analytic_or_invariant_tests: int = 2
    validation_tests: int = 3
    determinism_test: bool = True
    serialization_test: bool = True
    mission_tests: bool = True
    notebook_test: bool = True
    accessibility_test: bool = True
    numerical_convergence_test: bool = False


@dataclass(frozen=True, slots=True)
class ExpansionDefinition:
    """Static implementation manifest reviewed before registry enrollment."""

    metadata: SimulationDefinition
    subject: SubjectArea
    parameter_model: str
    result_model: str
    physics_entrypoint: str
    page_entrypoint: str
    canvas_entrypoint: str | None
    mode_requirements: tuple[ModeRequirements, ...]
    missions: tuple[MissionDefinition, ...]
    assumptions: tuple[ModelAssumption, ...]
    limitations: tuple[str, ...]
    accessibility: AccessibilityRequirements = AccessibilityRequirements()
    tests: TestRequirements = TestRequirements()


P = TypeVar("P", bound=ParameterSet)


@runtime_checkable
class ExpansionSimulation(Protocol, Generic[P]):
    """Pure-Python interface required from every expansion simulation."""

    metadata: SimulationDefinition
    model_version: str

    def run(self, parameters: P, *, seed: int = 0) -> ContractResult[P]:
        """Return deterministic results for identical parameters and seed."""

    def assumptions(self) -> tuple[ModelAssumption, ...]:
        """Return assumptions shown in Model mode and exported reports."""

    def outcome_text(self, result: ContractResult[P]) -> str:
        """Return a concise nonvisual description of the result."""
