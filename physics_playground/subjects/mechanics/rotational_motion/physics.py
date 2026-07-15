"""Pure constant-torque rotational-motion model."""
from dataclasses import dataclass
from enum import StrEnum
import math
from physics_playground.subjects.mechanics.common import require_finite
from physics_playground.validation import PhysicsValidationError
class BodyShape(StrEnum):POINT_MASS="Point mass";HOOP="Hoop";SOLID_DISK="Solid disk";SOLID_SPHERE="Solid sphere";ROD_CENTER="Rod about center"
FACTORS={BodyShape.POINT_MASS:1.,BodyShape.HOOP:1.,BodyShape.SOLID_DISK:.5,BodyShape.SOLID_SPHERE:.4,BodyShape.ROD_CENTER:1/12}
def moment_of_inertia(shape:BodyShape,mass_kg:float,radius_or_length_m:float)->float:return FACTORS[shape]*mass_kg*radius_or_length_m**2
@dataclass(frozen=True,slots=True)
class RotationalParameters:
    mass_kg:float=5.;radius_or_length_m:float=1.;shape:BodyShape=BodyShape.SOLID_DISK;torque_n_m:float=10.;initial_angular_velocity_rad_s:float=0.;duration_s:float=5.;samples:int=121
    def validate(self):
        require_finite(mass_kg=self.mass_kg,radius_or_length_m=self.radius_or_length_m,torque_n_m=self.torque_n_m,initial_angular_velocity_rad_s=self.initial_angular_velocity_rad_s,duration_s=self.duration_s)
        if self.mass_kg<=0 or self.radius_or_length_m<=0 or self.duration_s<=0:raise PhysicsValidationError("Mass, size, and duration must be greater than zero.")
        if not 2<=self.samples<=2000:raise PhysicsValidationError("Samples must be between 2 and 2000.")
        try:BodyShape(self.shape)
        except ValueError as exc:raise PhysicsValidationError("Choose a supported inertia model.") from exc
    def to_dict(self):return {**{k:getattr(self,k) for k in self.__dataclass_fields__},"shape":BodyShape(self.shape).value}
@dataclass(frozen=True,slots=True)
class RotationalResult:
    parameters:RotationalParameters;time_s:tuple[float,...];angular_position_rad:tuple[float,...];angular_velocity_rad_s:tuple[float,...];angular_acceleration_rad_s2:float;moment_of_inertia_kg_m2:float;rotational_kinetic_energy_j:tuple[float,...];work_done_j:tuple[float,...];outcome:str
def simulate(p:RotationalParameters)->RotationalResult:
    p.validate();shape=BodyShape(p.shape);inertia=moment_of_inertia(shape,p.mass_kg,p.radius_or_length_m);alpha=p.torque_n_m/inertia;time=tuple(p.duration_s*i/(p.samples-1) for i in range(p.samples));theta=tuple(p.initial_angular_velocity_rad_s*t+.5*alpha*t*t for t in time);omega=tuple(p.initial_angular_velocity_rad_s+alpha*t for t in time);ke=tuple(.5*inertia*w*w for w in omega);initial=ke[0];work=tuple(k-initial for k in ke)
    return RotationalResult(p,time,theta,omega,alpha,inertia,ke,work,f"The {shape.value.lower()} reaches {omega[-1]:.2f} rad/s after {p.duration_s:.1f} s.")
