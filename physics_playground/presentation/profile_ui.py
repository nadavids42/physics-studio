"""Streamlit controls and session synchronization for local profiles."""

from __future__ import annotations

import json
import logging

import streamlit as st

from physics_playground.accessibility_settings import AccessibilitySettings
from physics_playground.application_callbacks import ApplicationEvent
from physics_playground.education.progress import PathwayProgress
from physics_playground.missions.service import MissionProgress
from physics_playground.notebook import ExperimentNotebook
from physics_playground.profiles import LocalProfile, PersistenceUnavailable, ProfileStore
from physics_playground.registry import SIMULATION_REGISTRY, SIMULATIONS_BY_ID
from physics_playground.state_keys import SHARED_STATE_KEYS, feature_key, migrate_legacy_keys
from physics_playground.version import APPLICATION_VERSION

STORE_KEY = SHARED_STATE_KEYS.profiles_store
ACTIVE_KEY = SHARED_STATE_KEYS.profiles_active_id
FAVORITE_KEY = SHARED_STATE_KEYS.profiles_favorite_simulation
PERSISTENCE_ERROR_KEY = SHARED_STATE_KEYS.profiles_persistence_error
LOGGER = logging.getLogger(__name__)


def get_notebook() -> ExperimentNotebook:
    notebook = st.session_state.get(SHARED_STATE_KEYS.notebook)
    if isinstance(notebook, ExperimentNotebook):
        return notebook
    notebook = ExperimentNotebook()
    st.session_state[SHARED_STATE_KEYS.notebook] = notebook
    return notebook


def get_store():
    migrate_legacy_keys(st.session_state)
    if STORE_KEY in st.session_state:
        return st.session_state[STORE_KEY]
    try:
        store = ProfileStore()
    except PersistenceUnavailable as error:
        st.session_state[STORE_KEY] = None
        st.session_state[PERSISTENCE_ERROR_KEY] = str(error)
        return None
    st.session_state[STORE_KEY] = store
    return store


def load_into_session(profile: LocalProfile):
    st.session_state[ACTIVE_KEY] = profile.id
    progress = MissionProgress(completed=set(profile.badges_earned))
    st.session_state[SHARED_STATE_KEYS.missions_progress] = progress
    st.session_state[SHARED_STATE_KEYS.missions_completed] = progress.completed
    st.session_state[SHARED_STATE_KEYS.notebook] = ExperimentNotebook.from_dict(
        profile.trial_notebook or {}
    )
    st.session_state[SHARED_STATE_KEYS.accessibility_settings] = AccessibilitySettings.from_dict(
        profile.accessibility_settings
    )
    for name in (
        "audience_widget",
        "voice_widget",
        "mathematical_depth_widget",
        "visual_density_widget",
    ):
        st.session_state.pop(feature_key("accessibility", name), None)
    st.session_state[SHARED_STATE_KEYS.education_progress] = {
        lesson_id: PathwayProgress.from_dict(payload, lesson_id=lesson_id)
        for lesson_id, payload in profile.educational_progress.items()
    }
    st.session_state[SHARED_STATE_KEYS.navigation_active] = profile.last_used_simulation
    st.session_state[FAVORITE_KEY] = profile.favorite_simulation
    if profile.last_used_simulation:
        st.session_state[SHARED_STATE_KEYS.navigation_selector] = profile.last_used_simulation


def profile_from_session(existing: LocalProfile) -> LocalProfile:
    notebook = get_notebook()
    trials = notebook.trials
    last_parameters = {}
    for trial in trials:
        last_parameters[trial.simulation_id] = dict(trial.parameters)
    observations = tuple(trial.learner_observation for trial in trials if trial.learner_observation)
    progress = st.session_state.get(SHARED_STATE_KEYS.missions_progress, MissionProgress())
    pathway_progress = st.session_state.get(SHARED_STATE_KEYS.education_progress, {})
    return LocalProfile(
        id=existing.id,
        display_name=existing.display_name,
        badges_earned=tuple(sorted(progress.completed)),
        trial_notebook=json.loads(notebook.to_json()),
        last_used_simulation=st.session_state.get(SHARED_STATE_KEYS.navigation_active),
        last_used_parameters=last_parameters,
        favorite_simulation=st.session_state.get(FAVORITE_KEY),
        total_experiment_count=len(trials),
        learner_observations=observations,
        application_version=APPLICATION_VERSION,
        accessibility_settings=st.session_state.get(
            SHARED_STATE_KEYS.accessibility_settings, AccessibilitySettings()
        ).to_dict(),
        educational_progress={
            lesson_id: item.to_dict()
            for lesson_id, item in pathway_progress.items()
            if isinstance(item, PathwayProgress)
        },
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
        st.session_state[PERSISTENCE_ERROR_KEY] = str(error)
        LOGGER.warning("Could not persist the active profile: %s", error)
        return False


def persist_application_event(_event: ApplicationEvent) -> None:
    """Application-boundary subscriber for learning-state changes."""

    persist_active_session()


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
    st.subheader("Local learning profile")
    if not store:
        st.caption("Session-only mode: local persistence is unavailable.")
        if st.session_state.get(PERSISTENCE_ERROR_KEY):
            st.caption(st.session_state[PERSISTENCE_ERROR_KEY])
        return
    profiles = store.list_profiles()
    if not profiles:
        name = st.text_input("Display name", key=feature_key("profiles", "new_name_widget"))
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
        key=feature_key("profiles", "selector_widget"),
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
        key=feature_key("profiles", "favorite_widget"),
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
    upload = st.file_uploader(
        "Import profile", type="json", key=feature_key("profiles", "import_widget")
    )
    if upload and st.button("Import as new profile", use_container_width=True):
        profile = store.import_profile(upload.getvalue().decode("utf-8"))
        load_into_session(profile)
        st.rerun()
    with st.expander("Create another profile"):
        new_name = st.text_input(
            "New display name", key=feature_key("profiles", "additional_name_widget")
        )
        if st.button(
            "Create profile",
            disabled=not new_name.strip(),
            key=feature_key("profiles", "additional_create_widget"),
            use_container_width=True,
        ):
            persist_active_session()
            profile = store.create(new_name)
            load_into_session(profile)
            st.rerun()
    confirm = st.checkbox(
        "Reset this profile's progress", key=feature_key("profiles", "reset_confirm_widget")
    )
    if st.button("Reset profile", disabled=not confirm, use_container_width=True):
        profile = store.reset(current.id)
        load_into_session(profile)
        st.rerun()
