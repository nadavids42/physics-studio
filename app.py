"""Registry-driven Streamlit application shell."""

from __future__ import annotations

import streamlit as st

from physics_playground.application_callbacks import (
    ApplicationCallbacks,
    configure_application_callbacks,
)
from physics_playground.missions import ui as mission_ui
from physics_playground.presentation.accessibility_ui import (
    apply_global_accessibility,
    current_player_preferences,
    render_accessibility_panel,
)
from physics_playground.presentation.diagnostics import render_developer_diagnostics
from physics_playground.presentation.home import render_home
from physics_playground.presentation.notebook_ui import render_notebook_sidebar
from physics_playground.presentation.profile_ui import (
    persist_active_session,
    persist_application_event,
    render_profile_sidebar,
)
from physics_playground.presentation.titles import scientific_title
from physics_playground.registry import SIMULATION_REGISTRY, SIMULATIONS_BY_ID, load_validated_page
from physics_playground.state_keys import SHARED_STATE_KEYS, migrate_legacy_keys
from physics_playground.validation import PhysicsValidationError

st.set_page_config(page_title="Physics Studio", page_icon="⚛", layout="wide")
configure_application_callbacks(
    ApplicationCallbacks(
        on_event=persist_application_event,
        player_preferences=current_player_preferences,
    )
)
migrate_legacy_keys(st.session_state)
mission_ui.init_missions()
st.session_state.setdefault(SHARED_STATE_KEYS.navigation_active, None)
with st.sidebar:
    render_profile_sidebar()
    st.divider()
    accessibility_settings = render_accessibility_panel()
    st.divider()
    st.header("Navigation")
    navigation = ["home", *[item.id for item in SIMULATION_REGISTRY]]
    current = st.session_state[SHARED_STATE_KEYS.navigation_active] or "home"
    if SHARED_STATE_KEYS.navigation_selector not in st.session_state:
        st.session_state[SHARED_STATE_KEYS.navigation_selector] = (
            current if current in navigation else "home"
        )
    selected = st.radio(
        "Destination",
        navigation,
        format_func=lambda value: (
            "Physics Studio" if value == "home" else scientific_title(SIMULATIONS_BY_ID[value])
        ),
        label_visibility="collapsed",
        key=SHARED_STATE_KEYS.navigation_selector,
    )
    st.session_state[SHARED_STATE_KEYS.navigation_active] = None if selected == "home" else selected
    st.divider()
    st.subheader("Achievements")
    mission_ui.sidebar_badges()
    total = len(mission_ui.MISSION_LABELS)
    if len(st.session_state[SHARED_STATE_KEYS.missions_completed]) == total:
        st.success("All achievements completed.")
    st.divider()
    render_notebook_sidebar()
    render_developer_diagnostics()

apply_global_accessibility(accessibility_settings)

active = st.session_state[SHARED_STATE_KEYS.navigation_active]
if active is None:
    render_home()
else:
    module, entrypoint = load_validated_page(active)
    try:
        getattr(module, entrypoint)()
    except (PhysicsValidationError, FloatingPointError, OverflowError, MemoryError) as error:
        st.error(
            "This experiment could not finish safely. Try smaller values, fewer steps, or the recommended time step."
        )
        with st.expander("Technical details"):
            st.code(f"{type(error).__name__}: {error}")

persist_active_session()
