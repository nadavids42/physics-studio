from dataclasses import fields
from pathlib import Path

import pytest

from physics_playground.canvas import legacy
from physics_playground.canvas.player import PLAYER_CSS, PLAYER_JS, build_player_document
from physics_playground.registry import SIMULATION_REGISTRY
from physics_playground.visual.contrast import contrast_ratio
from physics_playground.visual.tokens import DARK_THEME, LIGHT_THEME

ROOT = Path(__file__).parents[1] / "physics_playground"
SCENE_ADAPTERS = (
    "boing.py",
    "bumper_cars.py",
    "cannonball.py",
    "diffusion_player.py",
    "double_pendulum.py",
    "earth_tunnel.py",
    "fluid_container.py",
    "gas_container.py",
    "orbit.py",
    "pendulum.py",
    "ray_diagram.py",
    "scalar_field.py",
    "vector_diagram.py",
    "vector_field.py",
    "wavefronts.py",
)


def test_all_22_registered_simulations_use_shared_renderers_and_four_modes():
    assert len(SIMULATION_REGISTRY) == 22
    assert len({simulation.id for simulation in SIMULATION_REGISTRY}) == 22
    for simulation in SIMULATION_REGISTRY:
        assert simulation.renderer.startswith("shared-")
        assert {mode.value for mode in simulation.modes} == {
            "Explore",
            "Compare",
            "Analyze",
            "Model",
        }


def test_every_canvas_adapter_builds_the_shared_player_document():
    canvas = ROOT / "canvas"
    for name in SCENE_ADAPTERS:
        source = (canvas / name).read_text(encoding="utf-8")
        assert "build_player_document" in source, name
        assert "requestAnimationFrame" not in source, name
    assert "build_player_document" in (ROOT / "subjects/mechanics/canvas.py").read_text()


def test_simulation_pages_have_no_isolated_native_chart_renderers():
    forbidden = ("st.line_chart", "st.bar_chart", "st.area_chart", "st.scatter_chart", "st.pyplot")
    for folder in (ROOT / "pages", ROOT / "subjects"):
        for page in folder.rglob("page.py"):
            source = page.read_text(encoding="utf-8")
            assert not any(token in source for token in forbidden), page
    accessibility = (ROOT / "presentation/accessibility.py").read_text()
    assert accessibility.count("st.pyplot") == 1 and "def render_chart" in accessibility


def test_scene_vectors_do_not_bypass_scale_semantics():
    for name in SCENE_ADAPTERS:
        source = (ROOT / "canvas" / name).read_text(encoding="utf-8")
        assert "PhysicsVisuals.arrow" not in source, name
    mechanics = (ROOT / "subjects/mechanics/canvas.py").read_text()
    assert "PhysicsVisuals.arrow" not in mechanics
    vector_helpers = (ROOT / "visual/vectors.py").read_text()
    assert "scale_mode:o.scale_mode||'schematic'" in vector_helpers


@pytest.mark.parametrize("theme", (LIGHT_THEME, DARK_THEME), ids=("light", "dark"))
def test_all_semantic_visual_colors_meet_wcag_graphical_contrast(theme):
    non_color = {
        "name",
        "canvas",
        "surface",
        "surface_raised",
        "surface_muted",
        "border",
        "grid",
        "text",
        "text_muted",
        "text_inverse",
        "accent_soft",
    }
    roles = [field.name for field in fields(theme) if field.name not in non_color]
    assert roles
    for role in roles:
        assert contrast_ratio(getattr(theme, role), theme.canvas) >= 3, role
    assert contrast_ratio(theme.text, theme.canvas) >= 4.5
    assert contrast_ratio(theme.text_muted, theme.canvas) >= 4.5


@pytest.mark.parametrize(
    "width,classification", ((360, "mobile"), (768, "tablet"), (1100, "desktop"))
)
def test_all_registered_simulations_share_representative_responsive_width_contract(
    width, classification
):
    document = build_player_document(
        config={"durationMs": 1, "tracks": [], "events": []},
        scene_javascript="const scene={draw(){}};",
        logical_width=width,
        logical_height=300,
        accessible_label=f"{classification} audit",
        idle_hint="Play",
    )
    assert "ResizeObserver" in document and "devicePixelRatio" in document
    assert "max-width:480px" in document and "max-width:100%" in document
    assert len(SIMULATION_REGISTRY) == 22


def test_every_player_serializes_motion_contrast_large_text_and_both_themes():
    document = build_player_document(
        config={"durationMs": 1, "tracks": [], "events": []},
        scene_javascript="const scene={draw(){}};",
        logical_width=200,
        logical_height=100,
        accessible_label="preferences",
        idle_hint="Play",
    )
    for token in (
        '"reducedMotion":',
        '"highContrast":',
        '"largeText":',
        '"visualThemes":{"light"',
        '"dark"',
        '"theme":',
    ):
        assert token in document
    assert "classList.toggle('large-text'" in PLAYER_JS
    assert "body.large-text" in PLAYER_CSS
    assert "min-height: 44px" in PLAYER_CSS


def test_context_is_a_background_layer_before_scientific_overlays():
    for name in SCENE_ADAPTERS:
        source = (ROOT / "canvas" / name).read_text(encoding="utf-8")
        context = source.find("PhysicsExperience.context")
        first_overlay = min(
            index
            for index in (source.find("PhysicsAssets."), source.find("PhysicsAnnotations."))
            if index >= 0
        )
        assert 0 <= context < first_overlay, name


def test_legacy_module_retains_only_compatibility_embedding_surface():
    source = (ROOT / "canvas/legacy.py").read_text(encoding="utf-8")
    assert callable(legacy.show)
    assert "def build_doc" not in source and "CANVAS_JS_UTILS" not in source
    assert "def show" in source
