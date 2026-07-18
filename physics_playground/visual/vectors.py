"""Semantic contracts and Canvas helpers for scientific vectors and annotations."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from enum import StrEnum

from physics_playground.frontend_assets import load_javascript_asset


class VectorScaleMode(StrEnum):
    PHYSICAL = "physical"  # length is quantitatively proportional to magnitude
    NORMALIZED = "normalized"  # direction is physical; length is adjusted for visibility
    SCHEMATIC = "schematic"  # explanatory direction only


DEFAULT_DISCLOSURES = {
    VectorScaleMode.NORMALIZED: "Vector lengths normalized for visibility",
    VectorScaleMode.SCHEMATIC: "Schematic vectors — not drawn to scale",
}


def linear_vector_scale(maximum_magnitude: float, maximum_length_px: float) -> float:
    """Return a zero-intercept pixel-per-unit scale for quantitative vectors."""

    if not math.isfinite(maximum_magnitude) or maximum_magnitude <= 0:
        raise ValueError("Maximum vector magnitude must be positive and finite.")
    if not math.isfinite(maximum_length_px) or maximum_length_px <= 0:
        raise ValueError("Maximum display length must be positive and finite.")
    return maximum_length_px / maximum_magnitude


@dataclass(frozen=True, slots=True)
class VectorSpec:
    x: float
    y: float
    dx: float
    dy: float
    role: str
    label: str = ""
    scale_mode: VectorScaleMode = VectorScaleMode.PHYSICAL
    pixels_per_unit: float | None = None
    units: str = ""
    fixed_length_px: float = 72
    dashed: bool = False
    disclosure: str = ""

    def __post_init__(self):
        values = (self.x, self.y, self.dx, self.dy, self.fixed_length_px)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Vector values must be finite.")
        if self.scale_mode is VectorScaleMode.PHYSICAL:
            if self.pixels_per_unit is None or self.pixels_per_unit <= 0:
                raise ValueError("Physically scaled vectors require positive pixels_per_unit.")
            if not self.units:
                raise ValueError("Physically scaled vectors require units.")
        elif self.fixed_length_px <= 0:
            raise ValueError("Nonphysical vector display length must be positive.")

    @property
    def magnitude(self) -> float:
        return math.hypot(self.dx, self.dy)

    @property
    def display_length_px(self) -> float:
        return (
            self.magnitude * self.pixels_per_unit
            if self.scale_mode is VectorScaleMode.PHYSICAL
            else self.fixed_length_px
        )

    @property
    def scale_disclosure(self) -> str:
        return self.disclosure or DEFAULT_DISCLOSURES.get(self.scale_mode, "")

    def to_dict(self):
        value = asdict(self)
        value["scale_mode"] = self.scale_mode.value
        value["scale_disclosure"] = self.scale_disclosure
        value["display_length_px"] = self.display_length_px
        return value


@dataclass(frozen=True, slots=True)
class ForceDiagramSpec:
    x: float
    y: float
    vectors: tuple[VectorSpec, ...]
    title: str = "Free-body diagram"

    def __post_init__(self):
        if any(vector.x != self.x or vector.y != self.y for vector in self.vectors):
            raise ValueError("Force-diagram vectors must share the diagram origin.")

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "title": self.title,
            "vectors": [item.to_dict() for item in self.vectors],
        }


CANVAS_VECTOR_JS = load_javascript_asset("physics-vectors.js")
