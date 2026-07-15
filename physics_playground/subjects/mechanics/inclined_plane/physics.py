"""Pure inclined-plane model with static and kinetic friction."""
from dataclasses import dataclass
import math
from physics_playground.subjects.mechanics.common import require_finite,weight
from physics_playground.validation import PhysicsValidationError

@dataclass(frozen=True,slots=True)
class InclinedPlaneParameters:
    mass_kg:float=2.0;angle_deg:float=30.0;static_friction:float=.3;kinetic_friction:float=.2
    gravity_m_s2:float=9.81;distance_m:float=5.0
    def validate(self):
        require_finite(mass_kg=self.mass_kg,angle_deg=self.angle_deg,static_friction=self.static_friction,kinetic_friction=self.kinetic_friction,gravity_m_s2=self.gravity_m_s2,distance_m=self.distance_m)
        if self.mass_kg<=0 or self.gravity_m_s2<=0 or self.distance_m<=0:raise PhysicsValidationError("Mass, gravity, and ramp distance must be greater than zero.")
        if not 0<=self.angle_deg<90:raise PhysicsValidationError("Ramp angle must be at least 0° and less than 90°.")
        if self.static_friction<0 or self.kinetic_friction<0:raise PhysicsValidationError("Friction coefficients cannot be negative.")
        if self.kinetic_friction>self.static_friction:raise PhysicsValidationError("Kinetic friction should not exceed static friction in this model.")
    def to_dict(self):return {name:getattr(self,name) for name in self.__dataclass_fields__}
@dataclass(frozen=True,slots=True)
class InclinedPlaneResult:
    parameters:InclinedPlaneParameters;moving:bool;normal_force_n:float;down_slope_force_n:float;friction_force_n:float;net_force_n:float;acceleration_m_s2:float;travel_time_s:float|None;final_speed_m_s:float;critical_angle_deg:float
    @property
    def outcome(self):return f"The block slides at {self.acceleration_m_s2:.2f} m/s²." if self.moving else "Static friction holds the block in place."
def simulate(p:InclinedPlaneParameters)->InclinedPlaneResult:
    p.validate();theta=math.radians(p.angle_deg);w=weight(p.mass_kg,p.gravity_m_s2);normal=w*math.cos(theta);down=w*math.sin(theta);limit=p.static_friction*normal;moving=down>limit+1e-12
    friction=p.kinetic_friction*normal if moving else down;net=max(0.0,down-friction);a=net/p.mass_kg
    time=math.sqrt(2*p.distance_m/a) if a>0 else None;speed=math.sqrt(2*a*p.distance_m) if a>0 else 0.0
    return InclinedPlaneResult(p,moving,normal,down,friction,net,a,time,speed,math.degrees(math.atan(p.static_friction)))
