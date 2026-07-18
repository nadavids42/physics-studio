from pathlib import Path

import pytest

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
