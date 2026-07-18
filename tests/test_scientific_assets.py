from dataclasses import FrozenInstanceError

import pytest

from physics_playground.canvas.player import build_player_document
from physics_playground.visual.assets import AssetKind, AssetSpec, AssetStyle, CANVAS_ASSET_JS


REQUIRED_ASSETS = {
    "sphere", "mass", "block", "cart", "pendulumBob", "pivot", "cable", "rod", "spring", "ramp",
    "pulley", "lever", "wheel", "planet", "moon", "star", "satellite", "projectile", "cannon",
    "fluidContainer", "fluidSurface", "lens", "mirror", "ray", "wavefront", "charge", "fieldLine",
    "forceArrow", "velocityArrow", "accelerationArrow", "torqueArc", "angleMarker", "ruler", "grid",
    "trail", "collisionFlash", "callout",
}


def test_asset_catalog_covers_every_required_scientific_primitive():
    assert {kind.value for kind in AssetKind} == REQUIRED_ASSETS
    for name in REQUIRED_ASSETS:
        assert name in CANVAS_ASSET_JS


def test_asset_spec_serializes_shared_configuration():
    spec = AssetSpec(AssetKind.BLOCK, 12, 34, width=80, height=45, scale=1.2, rotation=.4,
        label="Mass A", description="An 80 cm block on a ramp.",
        style=AssetStyle(fill="#123456", outline="#FFFFFF", opacity=.7, selected=True,
                         disabled=False, highlight=True, shadow=True, glow=False),
        options={"friction": .2})
    payload = spec.to_dict()
    assert payload["kind"] == "block"
    assert payload["x"] == 12 and payload["rotation"] == .4
    assert payload["style"]["selected"] is True
    assert payload["options"]["friction"] == .2
    assert spec.accessible_description == "An 80 cm block on a ramp."


def test_asset_spec_provides_practical_fallback_description_and_is_immutable():
    spec = AssetSpec(AssetKind.VELOCITY_ARROW, 1.5, -2, label="Velocity")
    assert spec.accessible_description == "Velocity at (1.5, -2)."
    with pytest.raises(FrozenInstanceError):
        spec.x = 3


def test_asset_library_has_shared_state_depth_and_semantic_rendering_hooks():
    for contract in ("o.selected", "o.disabled", "o.highlight", "o.shadow", "o.glow", "o.opacity", "o.rotation", "o.scale"):
        assert contract in CANVAS_ASSET_JS
    assert "createRadialGradient" in CANVAS_ASSET_JS
    assert "createLinearGradient" in CANVAS_ASSET_JS
    assert "V.token" in CANVAS_ASSET_JS
    assert "V.arrow" in CANVAS_ASSET_JS
    assert "function drawAll" in CANVAS_ASSET_JS


def test_asset_library_is_available_to_all_shared_player_scenes():
    document = build_player_document(config={"durationMs": 1, "tracks": [], "events": []},
        scene_javascript="const scene={draw(){}};", logical_width=100, logical_height=50,
        accessible_label="Asset test", idle_hint="Play")
    assert "const PhysicsAssets" in document
    assert "Unknown Physics Studio asset" in document
    assert "Object.freeze(Object.keys(library))" in document
