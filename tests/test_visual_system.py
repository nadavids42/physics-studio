from dataclasses import fields

import pytest

from physics_playground.canvas.player import build_player_document
from physics_playground.visual.contrast import contrast_ratio
from physics_playground.visual.css import shared_css, streamlit_css
from physics_playground.visual.tokens import (
    DARK_THEME,
    LIGHT_THEME,
    MOTION,
    RESPONSIVE,
    ThemeTokens,
    theme_payload,
)


def test_themes_have_identical_semantic_tokens():
    assert [item.name for item in fields(LIGHT_THEME)] == [item.name for item in fields(DARK_THEME)]
    assert isinstance(LIGHT_THEME, ThemeTokens)
    assert LIGHT_THEME.name == "light" and DARK_THEME.name == "dark"


@pytest.mark.parametrize("theme", [LIGHT_THEME, DARK_THEME])
def test_primary_text_and_status_colors_meet_wcag_contrast(theme):
    assert contrast_ratio(theme.text, theme.canvas) >= 4.5
    assert contrast_ratio(theme.text, theme.surface) >= 4.5
    assert contrast_ratio(theme.text_muted, theme.canvas) >= 4.5
    assert contrast_ratio(theme.warning, theme.canvas) >= 3
    assert contrast_ratio(theme.error, theme.canvas) >= 3


def test_css_includes_theme_motion_typography_and_responsive_rules():
    css = shared_css()
    assert "prefers-color-scheme:dark" in css
    assert "prefers-reduced-motion:reduce" in css
    assert "--ps-velocity" in css and "--ps-electric-field" in css
    assert "--ps-font-equation" in css
    assert f"max-width:{RESPONSIVE.mobile_max_px}px" in css
    assert f"--ps-duration-standard:{MOTION.standard_ms}ms" in css
    assert ".stApp" in streamlit_css()


def test_theme_payload_groups_tokens_for_renderers():
    payload = theme_payload(LIGHT_THEME)
    assert set(payload) == {"colors", "spacing", "shape", "typography", "motion", "responsive"}
    assert payload["colors"]["net_force"] == LIGHT_THEME.net_force
    assert payload["shape"]["trail_opacity"] > 0


def test_player_embeds_both_themes_and_shared_canvas_primitives():
    document = build_player_document(
        config={"durationMs": 1, "tracks": [], "events": []},
        scene_javascript="const scene={draw(){}};",
        logical_width=100,
        logical_height=50,
        accessible_label="Tokens",
        idle_hint="Play",
    )
    assert '"visualThemes":{"light"' in document
    assert "prefers-color-scheme: dark" in document
    assert "resolveVisualTheme" in document
    assert "globalThis.PhysicsVisuals" in document
    assert "function arrow" in document and "function grid" in document
