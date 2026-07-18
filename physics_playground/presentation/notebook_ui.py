"""Reusable Streamlit interface for the session experiment notebook."""

from __future__ import annotations

import streamlit as st

from physics_playground.notebook import ExperimentNotebook, TrialRecord
from physics_playground.setup_handoff import (
    SETUP_REQUEST_KEY,
    SimulationSetupRequest,
    queue_setup_request,
)
from physics_playground.state_keys import SHARED_STATE_KEYS, migrate_legacy_keys

NOTEBOOK_STATE_KEY = SHARED_STATE_KEYS.notebook
# Compatibility export retained for existing simulation pages.
REUSE_REQUEST_KEY = SETUP_REQUEST_KEY


def get_notebook() -> ExperimentNotebook:
    migrate_legacy_keys(st.session_state)
    if NOTEBOOK_STATE_KEY not in st.session_state:
        st.session_state[NOTEBOOK_STATE_KEY] = ExperimentNotebook()
    return st.session_state[NOTEBOOK_STATE_KEY]


def add_trial(**kwargs) -> TrialRecord:
    """Append a trial through the shared session notebook."""

    trial = get_notebook().add_trial(**kwargs)
    try:
        from physics_playground.presentation.profile_ui import persist_active_session

        persist_active_session()
    except Exception:
        pass
    return trial


def _trial_markdown(trial: TrialRecord, *, pinned: bool) -> None:
    pin = " 📌" if pinned else ""
    st.markdown(
        f"**Trial #{trial.trial_number}{pin} — {trial.simulation_id}**  \n{trial.result_summary}"
    )
    st.caption(f"{trial.timestamp} · model {trial.model_version} · seed {trial.random_seed}")
    if trial.learner_observation:
        st.markdown(f"> {trial.learner_observation}")


def render_notebook_sidebar() -> None:
    notebook = get_notebook()
    with st.expander(f"📓 Experiment notebook ({len(notebook.trials)})", expanded=False):
        if not notebook.trials:
            st.caption("Completed experiments will appear here.")
            return
        simulations = sorted({trial.simulation_id for trial in notebook.trials})
        selected_filter = st.selectbox(
            "Filter", ["All simulations", *simulations], key="notebook_filter"
        )
        visible = notebook.filtered(
            None if selected_filter == "All simulations" else selected_filter
        )
        labels = {trial.id: trial.display_label for trial in visible}
        selected_id = st.selectbox(
            "Selected trial", list(labels), format_func=labels.get, key="notebook_selected"
        )
        selected = notebook.get(selected_id)
        _trial_markdown(selected, pinned=notebook.pinned_run_a_id == selected.id)
        c1, c2 = st.columns(2)
        if c1.button("📌 Pin Run A", key="notebook_pin", use_container_width=True):
            notebook.pin(selected.id)
            st.rerun()
        if c2.button("↩ Reuse setup", key="notebook_reuse", use_container_width=True):
            queue_setup_request(
                st.session_state,
                SimulationSetupRequest(
                    simulation_id=selected.simulation_id,
                    parameters=selected.parameters,
                    source_label=f"Trial #{selected.trial_number}",
                    source_trial=selected.trial_number,
                ),
            )
            st.toast(f"Trial #{selected.trial_number} is ready to reuse.")
        if st.button("🗑 Delete selected", key="notebook_delete", use_container_width=True):
            notebook.delete(selected.id)
            st.rerun()

        if len(visible) >= 2:
            st.markdown("##### Compare two trials")
            ids = list(labels)
            default_a = (
                ids.index(notebook.pinned_run_a_id) if notebook.pinned_run_a_id in ids else 0
            )
            run_a = st.selectbox(
                "Run A", ids, index=default_a, format_func=labels.get, key="notebook_run_a"
            )
            run_b = st.selectbox(
                "Run B",
                ids,
                index=1 if default_a == 0 else 0,
                format_func=labels.get,
                key="notebook_run_b",
            )
            comparison = notebook.compare(run_a, run_b)
            if comparison.changed_parameters:
                changes = ", ".join(
                    f"{key}: {before} → {after}"
                    for key, (before, after) in comparison.changed_parameters.items()
                )
                st.caption(f"Changed: {changes}")
            for metric, delta in comparison.metric_deltas.items():
                st.markdown(f"- {metric}: **{delta:+.3f}**")

        st.download_button(
            "⬇ Export JSON",
            notebook.to_json(),
            "physics_trials.json",
            "application/json",
            use_container_width=True,
        )
        st.download_button(
            "⬇ Export CSV",
            notebook.to_csv(),
            "physics_trials.csv",
            "text/csv",
            use_container_width=True,
        )
        confirm = st.checkbox("I want to reset the notebook", key="notebook_reset_confirm")
        if st.button(
            "Reset notebook", disabled=not confirm, key="notebook_reset", use_container_width=True
        ):
            notebook.reset()
            st.rerun()
        from physics_playground.presentation.report_ui import render_report_builder

        render_report_builder(notebook)
