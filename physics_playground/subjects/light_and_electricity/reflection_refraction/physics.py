"""Pure planar reflection, Snell refraction, and total-internal-reflection model."""
from dataclasses import dataclass
import math
from physics_playground.subjects.light_and_electricity.common import RaySegment
from physics_playground.validation import PhysicsValidationError
@dataclass(frozen=True,slots=True)
class ReflectionRefractionParameters:
    incident_angle_deg:float=35.;refractive_index_1:float=1.;refractive_index_2:float=1.5
    def validate(self):
        if not all(math.isfinite(x) for x in (self.incident_angle_deg,self.refractive_index_1,self.refractive_index_2)):raise PhysicsValidationError("Angles and refractive indices must be finite.")
        if not 0<=self.incident_angle_deg<90:raise PhysicsValidationError("Incident angle must be from 0° up to, but not including, 90° from the normal.")
        if self.refractive_index_1<=0 or self.refractive_index_2<=0:raise PhysicsValidationError("Refractive indices must be greater than zero.")
    def to_dict(self):return {k:getattr(self,k) for k in self.__dataclass_fields__}
@dataclass(frozen=True,slots=True)
class ReflectionRefractionResult:
    parameters:ReflectionRefractionParameters;reflection_angle_deg:float;refraction_angle_deg:float|None;total_internal_reflection:bool;critical_angle_deg:float|None;rays:tuple[RaySegment,...];outcome:str
def simulate(p:ReflectionRefractionParameters)->ReflectionRefractionResult:
    p.validate();theta=math.radians(p.incident_angle_deg);ratio=p.refractive_index_1/p.refractive_index_2;argument=ratio*math.sin(theta);tir=argument>1+1e-12;critical=math.degrees(math.asin(p.refractive_index_2/p.refractive_index_1)) if p.refractive_index_1>p.refractive_index_2 else None;refracted=None if tir else math.degrees(math.asin(max(-1,min(1,argument))))
    length=4.;incident=RaySegment(-length*math.sin(theta),length*math.cos(theta),0,0,"Incident ray");reflected=RaySegment(0,0,length*math.sin(theta),length*math.cos(theta),"Reflected ray")
    rays=[incident,reflected]
    if not tir:
        t=math.radians(refracted);rays.append(RaySegment(0,0,length*math.sin(t),-length*math.cos(t),"Refracted ray"))
    outcome=f"Total internal reflection occurs; no transmitted ray enters medium 2." if tir else f"The ray reflects at {p.incident_angle_deg:.1f}° and refracts at {refracted:.1f}° from the normal."
    return ReflectionRefractionResult(p,p.incident_angle_deg,refracted,tir,critical,tuple(rays),outcome)
