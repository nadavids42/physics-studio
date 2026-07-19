"""Reusable Streamlit building blocks for the four-mode learning experience."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import TypeVar

import streamlit as st

from physics_playground.contracts import ModelAssumption, SummaryMetric
from physics_playground.models.simulations import LearningMode
from physics_playground.validation import PhysicsValidationError

R = TypeVar("R")

EXPECTED_MODEL_ERRORS = (PhysicsValidationError, FloatingPointError, OverflowError, MemoryError)

MODE_HELP = {
    LearningMode.EXPLORE: "Change simple controls, make a prediction, and launch the experiment.",
    LearningMode.COMPARE: "Keep a baseline and change one variable to see what it does.",
    LearningMode.ANALYZE: "Inspect graphs, measurements, and conservation diagnostics.",
    LearningMode.MODEL: "Look under the hood at equations, assumptions, and limitations.",
}


@dataclass(frozen=True, slots=True)
class ChangedVariable:
    label: str
    baseline: str
    modified: str


def mode_navigation(*, key: str) -> LearningMode:
    """Render a stable, version-friendly four-mode selector."""

    selected = st.radio(
        "Learning mode",
        [mode.value for mode in LearningMode],
        horizontal=True,
        key=key,
    )
    mode = LearningMode(selected)
    st.caption(MODE_HELP[mode])
    return mode


def mode_heading(mode: LearningMode, title: str) -> None:
    st.subheader(f"{mode.value}: {title}")


def run_model_safely(runner: Callable[[], R]) -> R | None:
    """Run a model call, reporting expected failures in place instead of crashing the page."""

    try:
        return runner()
    except EXPECTED_MODEL_ERRORS as error:
        st.error(
            "This experiment could not finish safely. Check the inputs and try values within "
            "the recommended ranges."
        )
        with st.expander("Technical details"):
            st.code(f"{type(error).__name__}: {error}")
        return None


def result_summary(metrics: Iterable[SummaryMetric], *, columns: int = 3) -> None:
    """Render contract metrics without requiring simulation-specific UI code."""

    values = tuple(metrics)
    if not values:
        st.info("Run the experiment to see its measurements.")
        return
    slots = st.columns(min(columns, len(values)))
    for index, metric in enumerate(values):
        display = metric.display_value or f"{metric.value:.3g} {metric.unit}".strip()
        slots[index % len(slots)].metric(metric.label, display, metric.comparison)


def changed_variable_banner(change: ChangedVariable) -> None:
    st.info(
        f"**Variable changed: {change.label}** — Run A: **{change.baseline}** → "
        f"Run B: **{change.modified}**"
    )


def comparison_metrics(
    baseline: Mapping[str, tuple[str, float]],
    modified: Mapping[str, tuple[str, float]],
) -> None:
    """Render shared numeric measurements for Run A and Run B."""

    rows = ["| Measurement | Run A | Run B | Change |", "|---|---:|---:|---:|"]
    for metric_id in baseline.keys() & modified.keys():
        label, value_a = baseline[metric_id]
        _, value_b = modified[metric_id]
        rows.append(f"| {label} | {value_a:.3f} | {value_b:.3f} | {value_b - value_a:+.3f} |")
    st.markdown("\n".join(rows))


def assumptions_panel(
    assumptions: Iterable[ModelAssumption],
    limitations: Iterable[str],
) -> None:
    st.markdown("#### Assumptions and simplifications")
    for assumption in assumptions:
        consequence = f" — {assumption.consequence}" if assumption.consequence else ""
        st.markdown(f"- **{assumption.statement}**{consequence}")
    st.markdown("#### Model limitations")
    for limitation in limitations:
        st.markdown(f"- {limitation}")
