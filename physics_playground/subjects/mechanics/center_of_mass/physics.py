"""Pure one-dimensional center-of-mass model for up to three objects."""

from dataclasses import dataclass

from physics_playground.subjects.mechanics.common import require_finite, weighted_position
from physics_playground.validation import PhysicsValidationError


@dataclass(frozen=True, slots=True)
class CenterOfMassParameters:
    mass_1_kg: float = 2.0
    position_1_m: float = -2.0
    mass_2_kg: float = 3.0
    position_2_m: float = 2.0
    mass_3_kg: float = 0.0
    position_3_m: float = 0.0

    def validate(self):
        require_finite(**{name: getattr(self, name) for name in self.__dataclass_fields__})
        if self.mass_1_kg < 0 or self.mass_2_kg < 0 or self.mass_3_kg < 0:
            raise PhysicsValidationError("Masses cannot be negative.")
        if self.mass_1_kg + self.mass_2_kg + self.mass_3_kg <= 0:
            raise PhysicsValidationError("At least one object must have positive mass.")

    def to_dict(self):
        return {name: getattr(self, name) for name in self.__dataclass_fields__}


@dataclass(frozen=True, slots=True)
class CenterOfMassResult:
    parameters: CenterOfMassParameters
    center_of_mass_m: float
    total_mass_kg: float
    left_mass_kg: float
    right_mass_kg: float
    outcome: str


def simulate(p: CenterOfMassParameters) -> CenterOfMassResult:
    p.validate()
    m = (p.mass_1_kg, p.mass_2_kg, p.mass_3_kg)
    x = (p.position_1_m, p.position_2_m, p.position_3_m)
    center = weighted_position(m, x)
    total = sum(m)
    left = sum(mass for mass, pos in zip(m, x, strict=True) if pos < center)
    right = sum(mass for mass, pos in zip(m, x, strict=True) if pos > center)
    return CenterOfMassResult(
        p,
        center,
        total,
        left,
        right,
        f"The system balances at x = {center:.2f} m, closer to the heavier or more distant masses.",
    )
