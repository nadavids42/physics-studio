"""Typed callbacks connecting domain changes to the application boundary.

This is intentionally a single callback seam, not a general-purpose event bus.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from physics_playground.education.models import EducationProgressEvent


@dataclass(frozen=True, slots=True)
class ProgressChanged:
    simulation_id: str
    completed_mission_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BadgeEarned:
    simulation_id: str
    mission_id: str


@dataclass(frozen=True, slots=True)
class NotebookChanged:
    trial_id: str


@dataclass(frozen=True, slots=True)
class AccessibilityChanged:
    reduced_motion: bool
    high_contrast: bool
    large_text: bool


ApplicationEvent = (
    ProgressChanged | BadgeEarned | NotebookChanged | AccessibilityChanged | EducationProgressEvent
)


@dataclass(frozen=True, slots=True)
class PlayerPreferences:
    reduced_motion: bool = False
    high_contrast: bool = False
    large_text: bool = False
    presentation_level: str = "illustrated"
    theme: str = "auto"


EventCallback = Callable[[ApplicationEvent], None]
PlayerPreferencesCallback = Callable[[], PlayerPreferences]


def _ignore_event(_event: ApplicationEvent) -> None:
    """Default used before the Streamlit application boundary is configured."""


def _default_player_preferences() -> PlayerPreferences:
    return PlayerPreferences()


@dataclass(frozen=True, slots=True)
class ApplicationCallbacks:
    on_event: EventCallback = _ignore_event
    player_preferences: PlayerPreferencesCallback = _default_player_preferences


_callbacks = ApplicationCallbacks()


def configure_application_callbacks(callbacks: ApplicationCallbacks) -> None:
    global _callbacks
    _callbacks = callbacks


def publish(event: ApplicationEvent) -> None:
    """Deliver synchronously; subscriber failures intentionally propagate."""

    _callbacks.on_event(event)


def get_player_preferences() -> PlayerPreferences:
    return _callbacks.player_preferences()


def reset_application_callbacks() -> None:
    """Restore safe defaults, primarily for isolated tests."""

    configure_application_callbacks(ApplicationCallbacks())
