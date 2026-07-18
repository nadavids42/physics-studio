"""Pure signed thin-lens model with principal-ray geometry."""

import math
from dataclasses import dataclass
from enum import StrEnum

from physics_playground.subjects.light_and_electricity.common import RaySegment
from physics_playground.validation import PhysicsValidationError


class LensType(StrEnum):
    CONVERGING = "Converging"
    DIVERGING = "Diverging"


@dataclass(frozen=True, slots=True)
class ThinLensParameters:
    object_distance_m: float = 3.0
    focal_length_m: float = 1.0
    object_height_m: float = 1.0

    def validate(self):
        if not all(
            math.isfinite(x)
            for x in (self.object_distance_m, self.focal_length_m, self.object_height_m)
        ):
            raise PhysicsValidationError("Lens parameters must be finite.")
        if self.object_distance_m <= 0:
            raise PhysicsValidationError("Object distance must be greater than zero.")
        if abs(self.focal_length_m) < 0.05:
            raise PhysicsValidationError(
                "Focal length must have magnitude of at least 0.05 m; use positive for converging and negative for diverging."
            )
        if self.object_height_m <= 0:
            raise PhysicsValidationError("Object height must be greater than zero.")

    def to_dict(self):
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


@dataclass(frozen=True, slots=True)
class ThinLensResult:
    parameters: ThinLensParameters
    lens_type: LensType
    image_distance_m: float | None
    magnification: float | None
    image_height_m: float | None
    real_image: bool | None
    inverted: bool | None
    singular: bool
    near_singular: bool
    rays: tuple[RaySegment, ...]
    outcome: str


def simulate(p: ThinLensParameters) -> ThinLensResult:
    p.validate()
    f = p.focal_length_m
    do = p.object_distance_m
    denominator = do - f
    scale = max(abs(do), abs(f), 1.0)
    singular = denominator == 0
    near = not singular and abs(denominator) <= 1e-4 * scale
    lens_type = LensType.CONVERGING if f > 0 else LensType.DIVERGING
    if singular:
        return ThinLensResult(
            p,
            lens_type,
            None,
            None,
            None,
            None,
            None,
            True,
            False,
            (),
            "The object is exactly at the focal point, so outgoing rays are parallel and the image is at infinity.",
        )
    di = f * do / denominator
    m = -di / do
    hi = m * p.object_height_m
    real = di > 0
    inverted = m < 0
    x_object = -do
    extent = max(2.0, min(10.0, abs(di)))
    rays = [
        RaySegment(x_object, p.object_height_m, 0, p.object_height_m, "Parallel principal ray"),
        RaySegment(x_object, p.object_height_m, 0, 0, "Central principal ray"),
    ]
    if real:
        rays.extend(
            (
                RaySegment(0, p.object_height_m, di, hi, "Through far focus"),
                RaySegment(0, 0, di, hi, "Undeviated central ray"),
            )
        )
    else:
        rays.extend(
            (
                RaySegment(
                    0,
                    p.object_height_m,
                    extent,
                    p.object_height_m - extent * p.object_height_m / f,
                    "Diverging ray",
                ),
                RaySegment(0, 0, extent, -extent * p.object_height_m / x_object, "Central ray"),
                RaySegment(0, p.object_height_m, di, hi, "Virtual extension", "virtual"),
                RaySegment(0, 0, di, hi, "Virtual central extension", "virtual"),
            )
        )
    qualifier = (
        "near the focal singularity, so the image distance and magnification are extremely sensitive"
        if near
        else ("real and inverted" if real else "virtual and upright")
    )
    return ThinLensResult(
        p,
        lens_type,
        di,
        m,
        hi,
        real,
        inverted,
        False,
        near,
        tuple(rays),
        f"The {lens_type.value.lower()} lens makes a {qualifier} image at {di:.2f} m with magnification {m:.2f}×.",
    )
