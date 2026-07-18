"""Presentation geometry derived from inclined-plane results without changing physics."""

from __future__ import annotations

import math

from physics_playground.visual.vectors import VectorScaleMode, VectorSpec, linear_vector_scale

from .physics import InclinedPlaneResult


def force_vectors(result: InclinedPlaneResult) -> tuple[list[dict[str, object]], float]:
    """Build one linearly scaled free-body diagram and return its px/N scale."""

    parameters = result.parameters
    weight_n = parameters.mass_kg * parameters.gravity_m_s2
    largest = max(
        weight_n,
        result.normal_force_n,
        result.friction_force_n,
        abs(result.net_force_n),
        1,
    )
    pixels_per_newton = linear_vector_scale(largest, 74)
    theta = math.radians(parameters.angle_deg)
    down = (math.cos(theta), -math.sin(theta))
    normal = (-math.sin(theta), math.cos(theta))

    def vector(
        dx: float, dy: float, role: str, label: str, *, dashed: bool = False
    ) -> dict[str, object]:
        return VectorSpec(
            0,
            0,
            dx,
            dy,
            role,
            label,
            VectorScaleMode.PHYSICAL,
            pixels_per_newton,
            "N",
            dashed=dashed,
        ).to_dict()

    vectors = [
        vector(0, -weight_n, "gravity", f"weight {weight_n:.1f} N"),
        vector(
            normal[0] * result.normal_force_n,
            normal[1] * result.normal_force_n,
            "normal_force",
            f"normal {result.normal_force_n:.1f} N",
        ),
    ]
    if result.friction_force_n:
        vectors.append(
            vector(
                -down[0] * result.friction_force_n,
                -down[1] * result.friction_force_n,
                "friction",
                f"{'kinetic' if result.moving else 'static'} friction "
                f"{result.friction_force_n:.1f} N",
            )
        )
    if abs(result.net_force_n) > 1e-9:
        vectors.append(
            vector(
                down[0] * result.net_force_n,
                down[1] * result.net_force_n,
                "net_force",
                f"resultant {result.net_force_n:.1f} N",
                dashed=True,
            )
        )
    return vectors, pixels_per_newton
