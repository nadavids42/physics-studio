"""Small, typed conventions for namespaced Streamlit session-state keys."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass
from typing import Any

STATE_PREFIX = "physics_studio"


def feature_key(feature: str, name: str) -> str:
    """Return a namespaced key owned by a cross-cutting feature."""

    if not feature or not name:
        raise ValueError("Session-state feature and name must be non-empty.")
    return f"{STATE_PREFIX}.{feature}.{name}"


def simulation_key(simulation_id: str, name: str) -> str:
    """Return the standard key for state owned by one simulation slice."""

    if not simulation_id or not name:
        raise ValueError("Simulation ID and state name must be non-empty.")
    return f"{STATE_PREFIX}.simulation.{simulation_id}.{name}"


@dataclass(frozen=True, slots=True)
class SharedStateKeys:
    navigation_active: str = feature_key("navigation", "active_simulation")
    navigation_selector: str = feature_key("navigation", "selector")
    accessibility_settings: str = feature_key("accessibility", "settings")
    accessibility_presentation_level: str = feature_key("accessibility", "presentation_level")
    accessibility_visual_preferences: str = feature_key("accessibility", "visual_preferences")
    missions_completed: str = feature_key("missions", "completed")
    missions_progress: str = feature_key("missions", "progress")
    notebook: str = feature_key("notebook", "trials")
    notebook_setup_request: str = feature_key("notebook", "setup_request")
    education_progress: str = feature_key("education", "pathway_progress")
    profiles_store: str = feature_key("profiles", "store")
    profiles_active_id: str = feature_key("profiles", "active_id")
    profiles_favorite_simulation: str = feature_key("profiles", "favorite_simulation")
    profiles_persistence_error: str = feature_key("profiles", "persistence_error")


SHARED_STATE_KEYS = SharedStateKeys()

LEGACY_SHARED_KEYS: Mapping[str, str] = {
    "active_simulation_id": SHARED_STATE_KEYS.navigation_active,
    "registry_navigation": SHARED_STATE_KEYS.navigation_selector,
    "accessibility_settings": SHARED_STATE_KEYS.accessibility_settings,
    "presentation_level": SHARED_STATE_KEYS.accessibility_presentation_level,
    "visual_preferences": SHARED_STATE_KEYS.accessibility_visual_preferences,
    "missions": SHARED_STATE_KEYS.missions_completed,
    "mission_progress": SHARED_STATE_KEYS.missions_progress,
    "experiment_notebook": SHARED_STATE_KEYS.notebook,
    "notebook_reuse_request": SHARED_STATE_KEYS.notebook_setup_request,
    "local_profile_store": SHARED_STATE_KEYS.profiles_store,
    "active_local_profile_id": SHARED_STATE_KEYS.profiles_active_id,
    "favorite_simulation_id": SHARED_STATE_KEYS.profiles_favorite_simulation,
    "persistence_error": SHARED_STATE_KEYS.profiles_persistence_error,
}


def migrate_legacy_keys(
    state: MutableMapping[str, Any],
    aliases: Mapping[str, str] = LEGACY_SHARED_KEYS,
) -> None:
    """Move known pre-namespace keys without overwriting canonical state."""

    for old_key, canonical_key in aliases.items():
        if old_key not in state:
            continue
        if canonical_key not in state:
            state[canonical_key] = state[old_key]
        del state[old_key]


def migrate_simulation_keys(
    state: MutableMapping[str, Any],
    simulation_id: str,
    aliases: Mapping[str, str],
) -> None:
    """Move page-local keys into one simulation namespace.

    ``aliases`` maps an old raw key to the new local name passed to
    :func:`simulation_key`.
    """

    migrate_legacy_keys(
        state,
        {old_key: simulation_key(simulation_id, name) for old_key, name in aliases.items()},
    )
