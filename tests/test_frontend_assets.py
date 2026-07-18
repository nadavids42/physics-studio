from pathlib import Path

import pytest

from physics_playground.canvas.player import PLAYER_JS
from physics_playground.frontend_assets import load_javascript_asset
from physics_playground.visual.primitives import CANVAS_VISUAL_JS


def test_built_visual_utility_is_loaded_as_a_packaged_asset() -> None:
    built = load_javascript_asset("physics-visuals.js")
    assert built == CANVAS_VISUAL_JS
    assert "globalThis.PhysicsVisuals" in built
    assert "responsive" in built


@pytest.mark.parametrize("name", ("", "../secret.js", "nested/file.js", "asset.css"))
def test_asset_loader_rejects_invalid_names(name: str) -> None:
    with pytest.raises(ValueError):
        load_javascript_asset(name)


def test_editable_visual_source_is_not_embedded_in_python() -> None:
    source = Path("physics_playground/visual/primitives.py").read_text()
    assert "load_javascript_asset" in source
    assert "const PhysicsVisuals" not in source


def test_shared_runtime_and_compatibility_assets_are_packaged() -> None:
    assert load_javascript_asset("player-runtime.js") == PLAYER_JS
    for name in (
        "physics-assets.js",
        "physics-vectors.js",
        "physics-animation.js",
        "physics-experience.js",
    ):
        assert load_javascript_asset(name)


def test_every_extracted_scene_asset_is_packaged() -> None:
    scene_assets = (
        "scene-boing.js",
        "scene-bumper-cars-comparison.js",
        "scene-bumper-cars.js",
        "scene-cannonball.js",
        "scene-diffusion-player.js",
        "scene-double-pendulum.js",
        "scene-earth-tunnel.js",
        "scene-fluid-container.js",
        "scene-gas-container.js",
        "scene-mechanics.js",
        "scene-orbital-gravity.js",
        "scene-pendulum.js",
        "scene-ray-diagram.js",
        "scene-scalar-field.js",
        "scene-vector-diagram.js",
        "scene-vector-field.js",
        "scene-wavefronts.js",
    )
    for name in scene_assets:
        assert "globalThis.scene" in load_javascript_asset(name)


def test_python_contains_no_editable_scene_javascript() -> None:
    root = Path("physics_playground")
    sources = "\n".join(path.read_text(encoding="utf-8") for path in root.rglob("*.py"))
    assert "const scene=" not in sources
    assert "const scene =" not in sources
