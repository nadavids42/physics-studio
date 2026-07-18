"""Pure magnetic-force models for moving charges and straight current elements."""

import math
from dataclasses import dataclass
from enum import StrEnum

from physics_playground.validation import PhysicsValidationError


class ForceMode(StrEnum):
    POINT_CHARGE = "Moving point charge"
    CURRENT_WIRE = "Current-carrying wire"


class ForceDirection(StrEnum):
    OUT_OF_SCREEN = "Out of screen ⊙"
    INTO_SCREEN = "Into screen ⊗"
    ZERO = "Zero force"


@dataclass(frozen=True, slots=True)
class MagneticForceParameters:
    mode: ForceMode = ForceMode.POINT_CHARGE
    charge_c: float = 1e-6
    velocity_m_s: float = 100.0
    current_a: float = 2.0
    wire_length_m: float = 0.5
    motion_angle_deg: float = 0.0
    magnetic_field_t: float = 0.2
    field_angle_deg: float = 90.0

    def validate(self):
        try:
            ForceMode(self.mode)
        except ValueError as exc:
            raise PhysicsValidationError("Choose a supported magnetic-force experiment.") from exc
        numeric = (
            self.charge_c,
            self.velocity_m_s,
            self.current_a,
            self.wire_length_m,
            self.motion_angle_deg,
            self.magnetic_field_t,
            self.field_angle_deg,
        )
        if not all(math.isfinite(x) for x in numeric):
            raise PhysicsValidationError("Magnetic-force parameters must be finite.")
        if self.velocity_m_s < 0 or self.wire_length_m <= 0 or self.magnetic_field_t < 0:
            raise PhysicsValidationError(
                "Speed and field magnitude cannot be negative; wire length must be positive."
            )
        if not -360 <= self.motion_angle_deg <= 360 or not -360 <= self.field_angle_deg <= 360:
            raise PhysicsValidationError("Vector angles must remain between −360° and 360°.")

    def to_dict(self):
        return {
            **{k: getattr(self, k) for k in self.__dataclass_fields__},
            "mode": ForceMode(self.mode).value,
        }


@dataclass(frozen=True, slots=True)
class MagneticForceResult:
    parameters: MagneticForceParameters
    mode: ForceMode
    relative_angle_deg: float
    sine_factor: float
    force_z_n: float
    force_magnitude_n: float
    direction: ForceDirection
    motion_vector: tuple[float, float]
    field_vector: tuple[float, float]
    right_hand_guidance: str
    outcome: str


def simulate(p: MagneticForceParameters) -> MagneticForceResult:
    p.validate()
    mode = ForceMode(p.mode)
    motion = math.radians(p.motion_angle_deg)
    field = math.radians(p.field_angle_deg)
    relative = math.radians(p.field_angle_deg - p.motion_angle_deg)
    cross = math.sin(relative)
    if mode is ForceMode.POINT_CHARGE:
        signed = p.charge_c * p.velocity_m_s * p.magnetic_field_t * cross
        guidance = "Point your fingers along velocity, curl toward the magnetic field, and use your thumb for the force on a positive charge. Reverse it for a negative charge."
    else:
        signed = p.current_a * p.wire_length_m * p.magnetic_field_t * cross
        guidance = "Point your fingers along conventional current, curl toward the magnetic field, and use your thumb for the wire's force. Negative current reverses the current vector."
    if abs(signed) < 1e-15:
        signed = 0.0
        direction = ForceDirection.ZERO
    else:
        direction = ForceDirection.OUT_OF_SCREEN if signed > 0 else ForceDirection.INTO_SCREEN
    motion_sign = -1 if mode is ForceMode.CURRENT_WIRE and p.current_a < 0 else 1
    mv = (motion_sign * math.cos(motion), motion_sign * math.sin(motion))
    bv = (math.cos(field), math.sin(field))
    relative_deg = ((p.field_angle_deg - p.motion_angle_deg + 180) % 360) - 180
    subject = "charge" if mode is ForceMode.POINT_CHARGE else "wire"
    outcome = (
        f"The {subject} feels {abs(signed):.3g} N {direction.value.lower()}."
        if signed
        else "The vectors are parallel or antiparallel, so the magnetic force is zero."
    )
    return MagneticForceResult(
        p, mode, relative_deg, cross, signed, abs(signed), direction, mv, bv, guidance, outcome
    )
