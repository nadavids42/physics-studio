"""Streamlit accessibility panel, global CSS, and chart rendering."""

from __future__ import annotations

import matplotlib as mpl
import streamlit as st
from cycler import cycler

from physics_playground.accessibility_settings import AccessibilitySettings
from physics_playground.application_callbacks import (
    AccessibilityChanged,
    PlayerPreferences,
    publish,
)
from physics_playground.education.audience import (
    AUDIENCE_DEFAULTS,
    AudienceLevel,
    AudiencePreferences,
    InstructionalVoice,
    MathematicalDepth,
    VisualDensity,
)
from physics_playground.presentation.chart_system import style_figure
from physics_playground.state_keys import SHARED_STATE_KEYS, feature_key, migrate_legacy_keys
from physics_playground.visual.css import streamlit_css
from physics_playground.visual.experience import (
    DEFAULT_PRESENTATION_LEVEL,
    PresentationLevel,
    VisualPreferences,
    VisualTheme,
)
from physics_playground.visual.tokens import LIGHT_THEME

SETTINGS_KEY = SHARED_STATE_KEYS.accessibility_settings
PRESENTATION_LEVEL_KEY = SHARED_STATE_KEYS.accessibility_presentation_level
VISUAL_PREFERENCES_KEY = SHARED_STATE_KEYS.accessibility_visual_preferences
VISUAL_THEME_WIDGET_KEY = feature_key("accessibility", "visual_theme_widget")
VISUAL_LEVEL_WIDGET_KEY = feature_key("accessibility", "presentation_level_widget")
AUDIENCE_WIDGET_KEY = feature_key("accessibility", "audience_widget")
VOICE_WIDGET_KEY = feature_key("accessibility", "voice_widget")
MATH_DEPTH_WIDGET_KEY = feature_key("accessibility", "mathematical_depth_widget")
VISUAL_DENSITY_WIDGET_KEY = feature_key("accessibility", "visual_density_widget")
VISUAL_SESSION_KEYS = frozenset(
    {
        PRESENTATION_LEVEL_KEY,
        VISUAL_PREFERENCES_KEY,
        VISUAL_THEME_WIDGET_KEY,
        VISUAL_LEVEL_WIDGET_KEY,
        AUDIENCE_WIDGET_KEY,
        VOICE_WIDGET_KEY,
        MATH_DEPTH_WIDGET_KEY,
        VISUAL_DENSITY_WIDGET_KEY,
    }
)
SAFE_COLORS = LIGHT_THEME.graph_colors
LINE_STYLES = ("-", "--", "-.", ":", "-", "--", "-.")
MARKERS = ("o", "s", "^", "D", "v", "P", "X")


def get_accessibility_settings():
    migrate_legacy_keys(st.session_state)
    value = st.session_state.get(SETTINGS_KEY)
    if isinstance(value, AccessibilitySettings):
        return value
    settings = AccessibilitySettings.from_dict(value or {})
    st.session_state[SETTINGS_KEY] = settings
    return settings


def get_presentation_level():
    return get_visual_preferences().presentation_level


def get_visual_preferences():
    stored = st.session_state.get(VISUAL_PREFERENCES_KEY)
    if stored is not None:
        return (
            stored if isinstance(stored, VisualPreferences) else VisualPreferences.from_dict(stored)
        )
    value = st.session_state.get(PRESENTATION_LEVEL_KEY, DEFAULT_PRESENTATION_LEVEL.value)
    try:
        level = PresentationLevel(value)
    except ValueError:
        level = DEFAULT_PRESENTATION_LEVEL
    preferences = VisualPreferences(level, VisualTheme.AUTO)
    st.session_state[VISUAL_PREFERENCES_KEY] = preferences.to_dict()
    return preferences


def render_accessibility_panel():
    current = get_accessibility_settings()
    with st.expander("Accessibility and presentation"):
        reduced = st.checkbox(
            "Reduce animation and disable autoplay",
            current.reduced_motion,
            key=feature_key("accessibility", "reduce_motion_widget"),
        )
        contrast = st.checkbox(
            "High-contrast display",
            current.high_contrast,
            key=feature_key("accessibility", "high_contrast_widget"),
        )
        large = st.checkbox(
            "Larger interface text",
            current.large_text,
            key=feature_key("accessibility", "large_text_widget"),
        )
        st.caption("Animation controls remain available in reduced-motion mode.")
        st.markdown("**Instructional profile**")

        def apply_audience_defaults() -> None:
            defaults = AUDIENCE_DEFAULTS[AudienceLevel(st.session_state[AUDIENCE_WIDGET_KEY])]
            st.session_state[VOICE_WIDGET_KEY] = defaults.voice.value
            st.session_state[MATH_DEPTH_WIDGET_KEY] = defaults.mathematical_depth.value
            st.session_state[VISUAL_DENSITY_WIDGET_KEY] = defaults.visual_density.value

        instruction = current.instructional
        audience = AudienceLevel(
            st.selectbox(
                "Audience",
                [item.value for item in AudienceLevel],
                index=list(AudienceLevel).index(instruction.audience),
                format_func=lambda value: value.title(),
                key=AUDIENCE_WIDGET_KEY,
                on_change=apply_audience_defaults,
                help="Explorer adds concrete scaffolding; Core is the default; Advanced emphasizes derivations, limitations, and numerical methods.",
            )
        )
        voice = InstructionalVoice(
            st.selectbox(
                "Voice",
                [item.value for item in InstructionalVoice],
                index=list(InstructionalVoice).index(instruction.voice),
                format_func=lambda value: value.title(),
                key=VOICE_WIDGET_KEY,
            )
        )
        mathematical_depth = MathematicalDepth(
            st.selectbox(
                "Mathematical depth",
                [item.value for item in MathematicalDepth],
                index=list(MathematicalDepth).index(instruction.mathematical_depth),
                format_func=lambda value: value.title(),
                key=MATH_DEPTH_WIDGET_KEY,
            )
        )
        visual_density = VisualDensity(
            st.selectbox(
                "Information density",
                [item.value for item in VisualDensity],
                index=list(VisualDensity).index(instruction.visual_density),
                format_func=lambda value: value.title(),
                key=VISUAL_DENSITY_WIDGET_KEY,
            )
        )
        preferences = get_visual_preferences()
        current_level = preferences.presentation_level
        level = PresentationLevel(
            st.selectbox(
                "Visual presentation",
                [item.value for item in PresentationLevel],
                index=list(PresentationLevel).index(current_level),
                format_func=lambda value: value.title(),
                key=VISUAL_LEVEL_WIDGET_KEY,
                help="Diagram maximizes clarity; Illustrated adds restrained depth; Contextual adds an optional real-world setting.",
            )
        )
        theme = VisualTheme(
            st.selectbox(
                "Visual theme",
                [item.value for item in VisualTheme],
                index=list(VisualTheme).index(preferences.theme),
                format_func=lambda value: value.title(),
                key=VISUAL_THEME_WIDGET_KEY,
                help="Auto follows the browser or operating-system theme.",
            )
        )
        st.session_state[PRESENTATION_LEVEL_KEY] = level.value
        st.session_state[VISUAL_PREFERENCES_KEY] = VisualPreferences(level, theme).to_dict()
    updated = AccessibilitySettings(
        reduced,
        contrast,
        large,
        AudiencePreferences(audience, voice, mathematical_depth, visual_density),
    )
    if updated != current:
        st.session_state[SETTINGS_KEY] = updated
        publish(AccessibilityChanged(reduced, contrast, large, updated.instructional.to_dict()))
    return updated


def current_player_preferences() -> PlayerPreferences:
    settings = get_accessibility_settings()
    preferences = get_visual_preferences()
    return PlayerPreferences(
        reduced_motion=settings.reduced_motion,
        high_contrast=settings.high_contrast,
        large_text=settings.large_text,
        presentation_level=preferences.presentation_level.value,
        theme=preferences.theme.value,
    )


def apply_global_accessibility(settings):
    text_size = "18px" if settings.large_text else "inherit"
    contrast = (
        """
    .stApp { background:#000 !important; color:#fff !important; }
    .stApp [data-testid="stSidebar"] { background:#111 !important; }
    a { color:#6EC6FF !important; text-decoration:underline !important; }
    """
        if settings.high_contrast
        else ""
    )
    st.markdown(
        f"""<style>{streamlit_css()}
    html,body,.stApp {{ max-width:100%; overflow-x:hidden; font-size:{text_size}; }}
    [data-testid="stHorizontalBlock"] {{ flex-wrap:wrap; }}
    button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,[role="radio"]:focus-visible {{ outline:3px solid #0072B2 !important; outline-offset:3px !important; }}
    iframe {{ max-width:100% !important; }}
    {contrast}
    </style>""",
        unsafe_allow_html=True,
    )
    mpl.rcParams["axes.prop_cycle"] = (
        cycler(color=SAFE_COLORS) + cycler(linestyle=LINE_STYLES) + cycler(marker=MARKERS)
    )


def render_chart(figure, caption):
    style_figure(figure, get_presentation_level())
    for axis in figure.axes:
        for index, line in enumerate(axis.lines):
            line.set_linestyle(LINE_STYLES[index % len(LINE_STYLES)])
            line.set_marker(MARKERS[index % len(MARKERS)])
            line.set_markevery(max(1, len(line.get_xdata()) // 12) if len(line.get_xdata()) else 1)
    st.pyplot(figure, use_container_width=True)
    st.caption(f"Chart description: {caption}")
