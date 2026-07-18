"""Small Streamlit adapters shared by the mechanics pages."""

import streamlit as st

from physics_playground.canvas import legacy
from physics_playground.presentation.notebook_ui import add_trial


def show(document):
    legacy.show(document, height=430)


def record(
    simulation_id,
    parameters,
    prediction,
    summary,
    metrics,
    badges,
    seed,
    version,
    observation,
    label=None,
):
    add_trial(
        simulation_id=simulation_id,
        parameters=parameters,
        prediction=prediction,
        result_summary=summary,
        metrics=metrics,
        earned_badges=badges,
        random_seed=seed,
        model_version=version,
        learner_observation=observation,
        label=label,
    )


def metric_table(metrics):
    columns = st.columns(min(3, len(metrics)))
    for index, (label, value) in enumerate(metrics.items()):
        columns[index % len(columns)].metric(label, value)
