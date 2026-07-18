"""Developer-facing diagnostics without exposing private learner data."""

import streamlit as st

from physics_playground.canvas.player import player_document_cache_info
from physics_playground.frontend_assets import frontend_asset_cache_info
from physics_playground.performance import (
    MAX_INTEGRATION_STEPS,
    MAX_NOTEBOOK_TRIALS,
    MAX_TRAJECTORY_SAMPLES,
    timing_snapshot,
)
from physics_playground.presentation.notebook_ui import get_notebook


def render_developer_diagnostics():
    with st.expander("🛠 Developer diagnostics"):
        st.caption("No learner names, observations, or parameter values are displayed here.")
        timings = timing_snapshot()
        st.metric("Notebook trials", f"{len(get_notebook().trials)}/{MAX_NOTEBOOK_TRIALS}")
        st.caption(
            f"Budgets: {MAX_TRAJECTORY_SAMPLES:,} trajectory samples; {MAX_INTEGRATION_STEPS:,} integration steps"
        )
        info = player_document_cache_info()
        st.caption(
            f"HTML document cache: {info.hits} hits, {info.misses} misses, {info.currsize} entries"
        )
        assets = frontend_asset_cache_info()
        st.caption(
            f"Frontend asset cache: {assets.hits} hits, {assets.misses} misses, "
            f"{assets.currsize}/{assets.maxsize} entries"
        )
        if not timings:
            st.info("No simulation timing samples have been recorded yet.")
        else:
            for item in timings[-10:]:
                st.markdown(f"- `{item['name']}`: {item['milliseconds']:.2f} ms ({item['source']})")
