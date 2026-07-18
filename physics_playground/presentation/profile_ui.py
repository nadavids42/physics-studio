"""Streamlit controls and session synchronization for local profiles."""

from __future__ import annotations

import json

import streamlit as st

from physics_playground.accessibility_settings import AccessibilitySettings
from physics_playground.missions.service import MissionProgress
from physics_playground.notebook import ExperimentNotebook
from physics_playground.presentation.accessibility_ui import SETTINGS_KEY
from physics_playground.presentation.notebook_ui import NOTEBOOK_STATE_KEY, get_notebook
from physics_playground.profiles import LocalProfile, PersistenceUnavailable, ProfileStore
from physics_playground.registry import SIMULATION_REGISTRY, SIMULATIONS_BY_ID
from physics_playground.version import APPLICATION_VERSION

STORE_KEY = "local_profile_store"
ACTIVE_KEY = "active_local_profile_id"
FAVORITE_KEY = "favorite_simulation_id"


def get_store():
    if STORE_KEY in st.session_state:
        return st.session_state[STORE_KEY]
    try:
        store = ProfileStore()
    except PersistenceUnavailable as error:
        st.session_state[STORE_KEY] = None
        st.session_state["persistence_error"] = str(error)
        return None
    st.session_state[STORE_KEY] = store
    return store


def load_into_session(profile: LocalProfile):
    st.session_state[ACTIVE_KEY] = profile.id
    progress = MissionProgress(completed=set(profile.badges_earned))
    st.session_state.mission_progress = progress
    st.session_state.missions = progress.completed
    st.session_state[NOTEBOOK_STATE_KEY] = ExperimentNotebook.from_dict(
        profile.trial_notebook or {}
    )
    st.session_state[SETTINGS_KEY] = AccessibilitySettings.from_dict(profile.accessibility_settings)
    st.session_state.active_simulation_id = profile.last_used_simulation
    st.session_state[FAVORITE_KEY] = profile.favorite_simulation
    if profile.last_used_simulation:
        st.session_state.registry_navigation = profile.last_used_simulation


def profile_from_session(existing: LocalProfile) -> LocalProfile:
    notebook = get_notebook()
    trials = notebook.trials
    last_parameters = {}
    for trial in trials:
        last_parameters[trial.simulation_id] = dict(trial.parameters)
    observations = tuple(trial.learner_observation for trial in trials if trial.learner_observation)
    progress = st.session_state.get("mission_progress", MissionProgress())
    return LocalProfile(
        id=existing.id,
        display_name=existing.display_name,
        badges_earned=tuple(sorted(progress.completed)),
        trial_notebook=json.loads(notebook.to_json()),
        last_used_simulation=st.session_state.get("active_simulation_id"),
        last_used_parameters=last_parameters,
        favorite_simulation=st.session_state.get(FAVORITE_KEY),
        total_experiment_count=len(trials),
        learner_observations=observations,
        application_version=APPLICATION_VERSION,
        accessibility_settings=st.session_state.get(
            SETTINGS_KEY, AccessibilitySettings()
        ).to_dict(),
    )


def persist_active_session():
    store = get_store()
    profile_id = st.session_state.get(ACTIVE_KEY)
    if not store or not profile_id:
        return False
    try:
        store.save(profile_from_session(store.load(profile_id)))
        return True
    except (OSError, KeyError, ValueError) as error:
        st.session_state["persistence_error"] = str(error)
        return False


def current_scientist_name():
    store = get_store()
    profile_id = st.session_state.get(ACTIVE_KEY)
    if not store or not profile_id:
        return "Scientist"
    try:
        return store.load(profile_id).display_name
    except KeyError:
        return "Scientist"


def render_profile_sidebar():
    store = get_store()
    st.subheader("👩‍🔬 Local scientist profile")
    if not store:
        st.caption("Session-only mode: local persistence is unavailable.")
        if st.session_state.get("persistence_error"):
            st.caption(st.session_state.persistence_error)
        return
    profiles = store.list_profiles()
    if not profiles:
        name = st.text_input("Scientist display name", key="new_profile_name")
        if st.button("Create local profile", disabled=not name.strip(), use_container_width=True):
            profile = store.create(name)
            load_into_session(profile)
            st.rerun()
        st.caption("Only a display name and learning progress are stored locally.")
        return
    ids = [profile.id for profile in profiles]
    labels = {p.id: p.display_name for p in profiles}
    active = st.session_state.get(ACTIVE_KEY)
    selected = st.selectbox(
        "Profile",
        ids,
        index=ids.index(active) if active in ids else 0,
        format_func=labels.get,
        key="profile_selector",
    )
    if active is None:
        load_into_session(store.load(selected))
        active = selected
    if selected != active and st.button("Switch profile", use_container_width=True):
        persist_active_session()
        load_into_session(store.load(selected))
        st.rerun()
    current = store.load(st.session_state[ACTIVE_KEY])
    favorite_options = [None, *[item.id for item in SIMULATION_REGISTRY]]
    stored_favorite = st.session_state.get(FAVORITE_KEY)
    favorite = st.selectbox(
        "Favorite simulation",
        favorite_options,
        index=favorite_options.index(stored_favorite) if stored_favorite in favorite_options else 0,
        format_func=lambda value: (
            "No favorite" if value is None else SIMULATIONS_BY_ID[value].navigation_label
        ),
        key="profile_favorite",
    )
    if favorite != st.session_state.get(FAVORITE_KEY):
        st.session_state[FAVORITE_KEY] = favorite
        persist_active_session()
    st.caption(
        f"{current.total_experiment_count} saved experiments · app {current.application_version}"
    )
    st.download_button(
        "Export profile",
        store.export_profile(current.id),
        f"{current.display_name}-physics-profile.json",
        "application/json",
        use_container_width=True,
    )
    upload = st.file_uploader("Import profile", type="json", key="profile_import")
    if upload and st.button("Import as new profile", use_container_width=True):
        profile = store.import_profile(upload.getvalue().decode("utf-8"))
        load_into_session(profile)
        st.rerun()
    with st.expander("Create another profile"):
        new_name = st.text_input("New scientist display name", key="additional_profile_name")
        if st.button(
            "Create profile",
            disabled=not new_name.strip(),
            key="additional_profile_create",
            use_container_width=True,
        ):
            persist_active_session()
            profile = store.create(new_name)
            load_into_session(profile)
            st.rerun()
    confirm = st.checkbox("Reset this profile's progress", key="profile_reset_confirm")
    if st.button("Reset profile", disabled=not confirm, use_container_width=True):
        profile = store.reset(current.id)
        load_into_session(profile)
        st.rerun()
