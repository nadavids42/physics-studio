"""Compatibility imports for the renamed accessibility UI module.

New code should import from :mod:`physics_playground.presentation.accessibility_ui`.
"""

from physics_playground.presentation.accessibility_ui import (
    LINE_STYLES,
    MARKERS,
    PRESENTATION_LEVEL_KEY,
    SAFE_COLORS,
    SETTINGS_KEY,
    VISUAL_LEVEL_WIDGET_KEY,
    VISUAL_PREFERENCES_KEY,
    VISUAL_SESSION_KEYS,
    VISUAL_THEME_WIDGET_KEY,
    apply_global_accessibility,
    get_accessibility_settings,
    get_presentation_level,
    get_visual_preferences,
    render_accessibility_panel,
    render_chart,
)

__all__ = [
    "LINE_STYLES",
    "MARKERS",
    "PRESENTATION_LEVEL_KEY",
    "SAFE_COLORS",
    "SETTINGS_KEY",
    "VISUAL_LEVEL_WIDGET_KEY",
    "VISUAL_PREFERENCES_KEY",
    "VISUAL_SESSION_KEYS",
    "VISUAL_THEME_WIDGET_KEY",
    "apply_global_accessibility",
    "get_accessibility_settings",
    "get_presentation_level",
    "get_visual_preferences",
    "render_accessibility_panel",
    "render_chart",
]
