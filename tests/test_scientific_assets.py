from dataclasses import FrozenInstanceError

import pytest

from physics_playground.visual.assets import AssetKind, AssetSpec, AssetStyle

REQUIRED_ASSETS = {
    "sphere",
    "mass",
    "block",
    "cart",
    "pendulumBob",
    "pivot",
    "cable",
    "rod",
    "spring",
    "ramp",
    "pulley",
    "lever",
    "track",
    "wheel",
    "planet",
    "moon",
    "star",
    "satellite",
    "projectile",
    "cannon",
    "source",
    "observer",
    "fluidContainer",
    "fluidSurface",
    "lens",
    "mirror",
    "ray",
    "wavefront",
    "charge",
    "fieldLine",
    "forceArrow",
    "velocityArrow",
    "accelerationArrow",
    "torqueArc",
    "angleMarker",
    "ruler",
    "grid",
    "trail",
    "collisionFlash",
    "callout",
}


def test_asset_catalog_covers_every_required_scientific_primitive():
    assert {kind.value for kind in AssetKind} == REQUIRED_ASSETS


def test_asset_spec_serializes_shared_configuration():
    spec = AssetSpec(
        AssetKind.BLOCK,
        12,
        34,
        width=80,
        height=45,
        scale=1.2,
        rotation=0.4,
        label="Mass A",
        description="An 80 cm block on a ramp.",
        style=AssetStyle(
            fill="#123456",
            outline="#FFFFFF",
            opacity=0.7,
            selected=True,
            disabled=False,
            highlight=True,
            shadow=True,
            glow=False,
        ),
        options={"friction": 0.2},
    )
    payload = spec.to_dict()
    assert payload["kind"] == "block"
    assert payload["x"] == 12 and payload["rotation"] == 0.4
    assert payload["style"]["selected"] is True
    assert payload["options"]["friction"] == 0.2
    assert spec.accessible_description == "An 80 cm block on a ramp."


def test_asset_spec_provides_practical_fallback_description_and_is_immutable():
    spec = AssetSpec(AssetKind.VELOCITY_ARROW, 1.5, -2, label="Velocity")
    assert spec.accessible_description == "Velocity at (1.5, -2)."
    with pytest.raises(FrozenInstanceError):
        spec.x = 3
