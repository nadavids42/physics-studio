"""Reusable Streamlit orchestration for typed simulation plugins."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any, Generic, TypeVar, cast

import streamlit as st

from physics_playground.contracts import (
    ContractResult,
    JsonValue,
    MissionEvaluation,
    ModelAssumption,
    ParameterSet,
)
from physics_playground.missions import ui as mission_ui
from physics_playground.presentation.learning_modes import (
    LearningMode,
    assumptions_panel,
    mode_navigation,
    result_summary,
)
from physics_playground.presentation.notebook_ui import add_trial
from physics_playground.simulation_plugin import SimulationPlugin
from physics_playground.state_keys import simulation_key
from physics_playground.validation import PhysicsValidationError

P = TypeVar("P", bound=ParameterSet)
R = TypeVar("R", bound=ContractResult[Any])
MissionContext = Mapping[str, JsonValue]
MissionHook = Callable[[R, MissionContext], tuple[MissionEvaluation, ...]]

EXPECTED_MODEL_ERRORS = (PhysicsValidationError, FloatingPointError, OverflowError, MemoryError)


class StreamlitSimulationRuntime(Generic[P, R]):
    """Own repeated Streamlit state and result orchestration for one plugin."""

    def __init__(
        self,
        plugin: SimulationPlugin[P, R],
        *,
        mission_hook: MissionHook[R] | None = None,
    ) -> None:
        self.plugin = plugin
        self.mission_hook = mission_hook

    def key(self, name: str) -> str:
        """Return a stable key and adopt the former raw page key when present."""

        canonical = cast(str, simulation_key(self.plugin.id, name))
        if name in st.session_state:
            if canonical not in st.session_state:
                st.session_state[canonical] = st.session_state[name]
            del st.session_state[name]
        return canonical

    def select_mode(self, *, key_name: str = "learning_mode") -> LearningMode:
        """Render the shared four-mode selector in this plugin's namespace."""

        return mode_navigation(key=self.key(key_name))

    def set_editing_parameters(self, parameters: P) -> None:
        st.session_state[self.key("editing_parameters")] = parameters

    def committed_parameters(self) -> P | None:
        value = st.session_state.get(self.key("committed_parameters"))
        return value if isinstance(value, self.plugin.parameter_type) else None

    def execute(self, parameters: P, *, commit: bool = False) -> R | None:
        """Safely execute editing parameters and optionally make them authoritative."""

        self.set_editing_parameters(parameters)
        try:
            parameters.validate()
            result = cast(R, self.plugin.model_runner(parameters))
        except EXPECTED_MODEL_ERRORS as error:
            st.error(
                "This experiment could not finish safely. Check the inputs and try values within the recommended ranges."
            )
            with st.expander("Technical details"):
                st.code(f"{type(error).__name__}: {error}")
            return None
        if commit:
            st.session_state[self.key("committed_parameters")] = parameters
            st.session_state[self.key("committed_model_version")] = self.plugin.model_version
        return result

    def render_result_summary(
        self,
        result: R,
        *,
        metric_ids: Iterable[str] | None = None,
        columns: int = 3,
    ) -> None:
        selected = None if metric_ids is None else set(metric_ids)
        metrics = (
            result.metrics
            if selected is None
            else tuple(metric for metric in result.metrics if metric.id in selected)
        )
        result_summary(metrics, columns=columns)

    def render_accessible_outcome(self, result: R) -> None:
        st.caption("Text outcome: " + self.plugin.accessible_summary(result))

    def process_missions(
        self,
        result: R,
        *,
        context: MissionContext | None = None,
    ) -> tuple[str, ...]:
        if self.mission_hook is None:
            return ()
        return cast(
            tuple[str, ...],
            mission_ui.process_run(self.plugin.id, self.mission_hook(result, context or {})),
        )

    def record_trial(
        self,
        result: R,
        *,
        seed: int,
        observation: str,
        prediction: str | None,
        label: str | None = None,
        earned_badges: tuple[str, ...] = (),
        parameter_extras: Mapping[str, JsonValue] | None = None,
        summary: str | None = None,
        metrics: Mapping[str, float] | None = None,
    ) -> None:
        parameters = self.plugin.serialize_notebook_parameters(result.parameters)
        if parameter_extras:
            parameters = {**parameters, **parameter_extras}
        add_trial(
            simulation_id=self.plugin.id,
            parameters=parameters,
            prediction=prediction,
            result_summary=summary or self.plugin.accessible_summary(result),
            metrics=metrics or {metric.id: metric.value for metric in result.metrics},
            earned_badges=earned_badges,
            random_seed=seed,
            model_version=self.plugin.model_version,
            learner_observation=observation,
            label=label,
        )

    def render_assumptions_and_limitations(
        self,
        assumptions: Iterable[ModelAssumption],
        limitations: Iterable[str],
    ) -> None:
        assumptions_panel(assumptions, limitations)

    def prediction(self, name: str) -> str | None:
        value = st.session_state.get(self.key(name))
        return value if isinstance(value, str) else None

    @staticmethod
    def rerun() -> None:
        st.rerun()
