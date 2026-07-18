"""Stable structural and semantic regression tests for the shared visual system."""

import ast
import hashlib
import json
from dataclasses import fields
from pathlib import Path

import pytest

from physics_playground.canvas.player import PLAYER_JS, build_player_document
from physics_playground.presentation.accessibility_ui import SETTINGS_KEY, VISUAL_SESSION_KEYS
from physics_playground.visual.assets import AssetKind, AssetSpec, AssetStyle
from physics_playground.visual.experience import PresentationLevel, VisualPreferences, VisualTheme
from physics_playground.visual.primitives import CANVAS_VISUAL_JS
from physics_playground.visual.tokens import (
    DARK_THEME,
    LIGHT_THEME,
    MOTION,
    RESPONSIVE,
    SHAPE,
    SPACING,
    TYPOGRAPHY,
    theme_payload,
)
from physics_playground.visual.vectors import VectorScaleMode, VectorSpec


def test_design_token_groups_are_available_and_palette_shapes_match():
    payload = theme_payload(LIGHT_THEME)
    assert set(payload) == {"colors", "spacing", "shape", "typography", "motion", "responsive"}
    assert all(fields(group) for group in (SPACING, SHAPE, TYPOGRAPHY, MOTION, RESPONSIVE))
    assert [field.name for field in fields(LIGHT_THEME)] == [
        field.name for field in fields(DARK_THEME)
    ]
    for theme in (LIGHT_THEME, DARK_THEME):
        colors = [getattr(theme, field.name) for field in fields(theme) if field.name != "name"]
        assert all(color.startswith("#") and len(color) == 7 for color in colors)
        assert len(set(theme.graph_colors)) == len(theme.graph_colors)


def test_shared_asset_configuration_semantic_golden_snapshot():
    assets = (
        AssetSpec(
            AssetKind.BLOCK,
            20,
            30,
            width=60,
            height=40,
            label="Block A",
            style=AssetStyle(selected=True),
        ),
        AssetSpec(
            AssetKind.FORCE_ARROW,
            20,
            30,
            width=80,
            label="Net force",
            style=AssetStyle(shadow=False),
            options={"scale_mode": "schematic"},
        ),
    )
    canonical = json.dumps(
        [asset.to_dict() for asset in assets], sort_keys=True, separators=(",", ":")
    )
    assert (
        hashlib.sha256(canonical.encode()).hexdigest()
        == "60a597853f53bda99ecfb60d2ad5c693d2013f47e39a903d1705d121e4a29e5c"
    )
    assert assets[0].accessible_description == "Block A at (20, 30)."


def test_vector_display_geometry_for_all_scaling_modes():
    physical = VectorSpec(0, 0, 3, 4, "velocity", pixels_per_unit=6, units="m/s")
    normalized = VectorSpec(
        0, 0, 30, 40, "velocity", scale_mode=VectorScaleMode.NORMALIZED, fixed_length_px=72
    )
    schematic = VectorSpec(
        0, 0, 0.1, 0.1, "net_force", scale_mode=VectorScaleMode.SCHEMATIC, fixed_length_px=48
    )
    assert physical.display_length_px == 30
    assert normalized.display_length_px == 72
    assert schematic.display_length_px == 48
    assert normalized.scale_disclosure and schematic.scale_disclosure


def test_high_dpi_canvas_is_scaled_and_bounded():
    assert "window.devicePixelRatio" in PLAYER_JS
    assert "maximumDpr||2.5" in PLAYER_JS
    assert "Math.round(this.cssWidth*dpr)" in PLAYER_JS
    assert "this.ctx.setTransform(dpr,0,0,dpr,0,0)" in PLAYER_JS


def test_reduced_motion_disables_autoplay_and_decorative_motion_only():
    document = build_player_document(
        config={"durationMs": 1000, "autoplay": True, "tracks": [], "events": []},
        scene_javascript="const scene={draw(){}};",
        logical_width=200,
        logical_height=100,
        accessible_label="Reduced motion",
        idle_hint="Play",
    )
    assert "prefers-reduced-motion:reduce" in document
    assert "if(config.autoplay && !this.reducedMotion)" in document
    assert "if (this.reducedMotion) return" in document
    assert 'id="step-forward"' in document and 'id="scrubber"' in document


@pytest.mark.parametrize("theme", list(VisualTheme))
def test_theme_switching_is_serialized_into_deterministic_player_input(theme):
    config = {"durationMs": 1, "tracks": [], "events": [], "theme": theme.value}
    kwargs = dict(
        scene_javascript="const scene={draw(){}};",
        logical_width=100,
        logical_height=50,
        accessible_label="Theme",
        idle_hint="Play",
    )
    first = build_player_document(config=config, **kwargs)
    second = build_player_document(config=config, **kwargs)
    assert first == second
    assert f'"theme":"{theme.value}"' in first
    assert '"visualThemes":{"light"' in first and '"dark"' in first


def test_visual_preferences_round_trip_and_invalid_values_fall_back():
    preferences = VisualPreferences(PresentationLevel.CONTEXTUAL, VisualTheme.DARK)
    assert VisualPreferences.from_dict(preferences.to_dict()) == preferences
    assert (
        VisualPreferences.from_dict({"presentation_level": "unknown", "theme": "unknown"})
        == VisualPreferences()
    )


def test_responsive_layout_contract_has_ordered_breakpoints_and_canvas_helper():
    assert 0 < RESPONSIVE.mobile_max_px < RESPONSIVE.tablet_max_px < RESPONSIVE.content_max_px
    assert RESPONSIVE.control_target_px >= 44
    assert "return w<=(r.mobile_max_px||480)?'mobile'" in CANVAS_VISUAL_JS
    assert "img,svg,canvas,iframe {max-width:100%;}" in build_player_document(
        config={"durationMs": 1, "tracks": [], "events": []},
        scene_javascript="const scene={draw(){}};",
        logical_width=100,
        logical_height=50,
        accessible_label="Responsive",
        idle_hint="Play",
    )


def _existing_session_keys() -> set[str]:
    root = Path(__file__).parents[1] / "physics_playground"
    keys = set()
    for path in root.rglob("*.py"):
        if path.name == "accessibility_ui.py" and path.parent.name == "presentation":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Subscript)
                and isinstance(node.slice, ast.Constant)
                and isinstance(node.slice.value, str)
            ):
                keys.add(node.slice.value)
            if isinstance(node, ast.Call):
                for keyword in node.keywords:
                    if (
                        keyword.arg == "key"
                        and isinstance(keyword.value, ast.Constant)
                        and isinstance(keyword.value.value, str)
                    ):
                        keys.add(keyword.value.value)
    return keys


def test_visual_session_state_keys_are_unique_and_do_not_collide_with_existing_keys():
    assert len(VISUAL_SESSION_KEYS) == 4
    assert SETTINGS_KEY not in VISUAL_SESSION_KEYS
    assert VISUAL_SESSION_KEYS.isdisjoint(_existing_session_keys())


def test_pilot_scene_semantic_golden_signatures():
    from physics_playground.canvas import bumper_cars, orbit, ray_diagram
    from physics_playground.subjects.mechanics.cannonball import scene as cannonball
    from physics_playground.subjects.waves_and_oscillations.pendulum import scene as pendulum

    signatures = {
        "projectile": (
            "PhysicsAssets.cannon",
            "PhysicsAssets.projectile",
            "PhysicsAnimation.fadingTrail",
        ),
        "pendulum": ("PhysicsAssets.pivot", "PhysicsAssets.cable", "PhysicsAssets.pendulumBob"),
        "orbit": ("PhysicsAssets.star", "PhysicsAssets.planet", "PhysicsAnimation.fadingTrail"),
        "collision": (
            "PhysicsAssets.cart",
            "PhysicsAnimation.impactRipple",
            "PhysicsAnimation.collisionFlash",
        ),
        "optics": ("PhysicsAssets.lens", "PhysicsAssets.ray", "PhysicsAnnotations.normalLine"),
    }
    sources = {
        "projectile": cannonball.SCENE,
        "pendulum": pendulum.SCENE,
        "orbit": orbit.SCENE,
        "collision": bumper_cars.SCENE_JAVASCRIPT,
        "optics": ray_diagram.SCENE,
    }
    actual = {
        name: tuple(token for token in expected if token in sources[name])
        for name, expected in signatures.items()
    }
    assert actual == signatures
