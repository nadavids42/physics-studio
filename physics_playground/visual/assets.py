"""Typed asset contracts and the shared Canvas scientific asset library.

Physics remains renderer-neutral: an ``AssetSpec`` can be serialized into a
scene payload, described as text, or drawn by ``PhysicsAssets`` in the browser.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any

from physics_playground.frontend_assets import load_javascript_asset


class AssetKind(StrEnum):
    SPHERE = "sphere"
    MASS = "mass"
    BLOCK = "block"
    CART = "cart"
    PENDULUM_BOB = "pendulumBob"
    PIVOT = "pivot"
    CABLE = "cable"
    ROD = "rod"
    SPRING = "spring"
    RAMP = "ramp"
    PULLEY = "pulley"
    LEVER = "lever"
    TRACK = "track"
    WHEEL = "wheel"
    PLANET = "planet"
    MOON = "moon"
    STAR = "star"
    SATELLITE = "satellite"
    PROJECTILE = "projectile"
    CANNON = "cannon"
    SOURCE = "source"
    OBSERVER = "observer"
    FLUID_CONTAINER = "fluidContainer"
    FLUID_SURFACE = "fluidSurface"
    LENS = "lens"
    MIRROR = "mirror"
    RAY = "ray"
    WAVEFRONT = "wavefront"
    CHARGE = "charge"
    FIELD_LINE = "fieldLine"
    FORCE_ARROW = "forceArrow"
    VELOCITY_ARROW = "velocityArrow"
    ACCELERATION_ARROW = "accelerationArrow"
    TORQUE_ARC = "torqueArc"
    ANGLE_MARKER = "angleMarker"
    RULER = "ruler"
    GRID = "grid"
    TRAIL = "trail"
    COLLISION_FLASH = "collisionFlash"
    CALLOUT = "callout"


@dataclass(frozen=True, slots=True)
class AssetStyle:
    fill: str | None = None
    outline: str | None = None
    opacity: float = 1
    selected: bool = False
    disabled: bool = False
    highlight: bool = False
    shadow: bool = True
    glow: bool = False


@dataclass(frozen=True, slots=True)
class AssetSpec:
    kind: AssetKind
    x: float
    y: float
    width: float = 40
    height: float = 40
    scale: float = 1
    rotation: float = 0
    label: str = ""
    description: str = ""
    style: AssetStyle = field(default_factory=AssetStyle)
    options: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["kind"] = self.kind.value
        return payload

    @property
    def accessible_description(self) -> str:
        if self.description:
            return self.description
        name = self.label or self.kind.value.replace("Arrow", " arrow").replace("Line", " line")
        return f"{name} at ({self.x:g}, {self.y:g})."


CANVAS_ASSET_JS = load_javascript_asset("physics-assets.js")
