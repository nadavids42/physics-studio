"""Registry-driven Streamlit application shell."""

from __future__ import annotations

import streamlit as st

from physics_playground.application_callbacks import (
    ApplicationCallbacks,
    configure_application_callbacks,
)
from physics_playground.education.catalog import LESSONS_BY_ID
from physics_playground.missions import ui as mission_ui
from physics_playground.performance import timing_block
from physics_playground.presentation.accessibility_ui import (
    apply_global_accessibility,
    current_player_preferences,
    render_accessibility_panel,
)
from physics_playground.presentation.diagnostics import render_developer_diagnostics
from physics_playground.presentation.home import render_home
from physics_playground.presentation.navigation import (
    NAVIGATION_SUBJECTS,
    SUBJECTS_BY_ID,
    recommended_lesson,
)
from physics_playground.presentation.notebook_ui import render_notebook_sidebar
from physics_playground.presentation.profile_ui import (
    persist_active_session,
    persist_application_event,
    render_profile_sidebar,
)
from physics_playground.registry import SIMULATIONS_BY_ID, load_validated_page
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
st.session_state.setdefault(SHARED_STATE_KEYS.navigation_active_lesson, None)


def show_home(subject_id: str | None = None) -> None:
    st.session_state[SHARED_STATE_KEYS.navigation_active] = None
    st.session_state[SHARED_STATE_KEYS.navigation_active_lesson] = None
    if subject_id:
        st.session_state[SHARED_STATE_KEYS.navigation_subject_filter] = subject_id
    st.query_params.clear()


def open_lesson(simulation_id: str, lesson_id: str) -> None:
    st.session_state[SHARED_STATE_KEYS.navigation_active] = simulation_id
    st.session_state[SHARED_STATE_KEYS.navigation_active_lesson] = lesson_id
    st.query_params["simulation"] = simulation_id
    st.query_params["lesson"] = lesson_id


with st.sidebar:
    render_profile_sidebar()
    st.divider()
    accessibility_settings = render_accessibility_panel()
    st.divider()
    st.header("Navigation")
    st.button(
        "Home and discovery",
        use_container_width=True,
        type="primary"
        if st.session_state[SHARED_STATE_KEYS.navigation_active] is None
        else "secondary",
        on_click=show_home,
    )
    subject_ids = ["all", *[subject.id for subject in NAVIGATION_SUBJECTS]]
    selected_subject = st.selectbox(
        "Browse by subject",
        subject_ids,
        format_func=lambda value: "All subjects" if value == "all" else SUBJECTS_BY_ID[value].title,
        key=SHARED_STATE_KEYS.navigation_subject_filter,
    )
    subject = SUBJECTS_BY_ID.get(selected_subject)
    unit_options = [*subject.units, "Simulations"] if subject else ["All units and collections"]
    selected_unit = st.selectbox("Unit or collection", unit_options)
    concepts = (
        subject.concepts
        if subject
        else tuple(sorted({concept for item in NAVIGATION_SUBJECTS for concept in item.concepts}))
    )
    concept_options = ["All concepts", *concepts]
    st.selectbox(
        "Concept",
        concept_options,
        key=SHARED_STATE_KEYS.navigation_concept_filter,
    )
    st.button(
        "Browse this subject on home",
        use_container_width=True,
        on_click=show_home,
        args=(selected_subject,),
        help=f"Show {selected_unit.lower()} without restricting access to other subjects.",
    )
    recommendation = recommended_lesson(
        st.session_state.get(SHARED_STATE_KEYS.education_progress, {})
    )
    if recommendation:
        st.markdown("**Recommended next**")
        st.caption(recommendation.title)
        st.button(
            "Open recommended lesson",
            key="sidebar_recommended_lesson",
            use_container_width=True,
            on_click=open_lesson,
            args=(recommendation.simulation_ids[0], recommendation.id),
        )
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

# URL targets are applied after profile restoration so a shared link remains authoritative.
query_simulation = st.query_params.get("simulation")
if query_simulation in SIMULATIONS_BY_ID:
    st.session_state[SHARED_STATE_KEYS.navigation_active] = query_simulation
query_lesson = st.query_params.get("lesson")
if (
    isinstance(query_lesson, str)
    and query_lesson in LESSONS_BY_ID
    and query_simulation in LESSONS_BY_ID[query_lesson].simulation_ids
):
    st.session_state[SHARED_STATE_KEYS.navigation_active_lesson] = query_lesson

active = st.session_state[SHARED_STATE_KEYS.navigation_active]
if active is None:
    render_home()
else:
    if st.button("← Back to discovery", on_click=show_home):
        st.stop()
    module, entrypoint = load_validated_page(active)
    try:
        with timing_block(f"page.{active}"):
            getattr(module, entrypoint)()
    except (PhysicsValidationError, FloatingPointError, OverflowError, MemoryError) as error:
        st.error(
            "This experiment could not finish safely. Try smaller values, fewer steps, or the recommended time step."
        )
        with st.expander("Technical details"):
            st.code(f"{type(error).__name__}: {error}")

persist_active_session()
