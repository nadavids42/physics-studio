"""Pure energy-based roller-coaster model over a piecewise-linear track."""
from dataclasses import dataclass
import math
from physics_playground.subjects.mechanics.common import require_finite
from physics_playground.validation import PhysicsValidationError
@dataclass(frozen=True,slots=True)
class RollerCoasterParameters:
    mass_kg:float=200.;initial_height_m:float=20.;initial_speed_m_s:float=0.;hill_height_m:float=12.;final_height_m:float=2.;track_length_m:float=80.;loss_per_meter_j:float=0.;gravity_m_s2:float=9.81;samples:int=161
    def validate(self):
        require_finite(**{k:float(getattr(self,k)) for k in self.__dataclass_fields__ if k!="samples"})
        if self.mass_kg<=0 or self.gravity_m_s2<=0 or self.track_length_m<=0:raise PhysicsValidationError("Mass, gravity, and track length must be greater than zero.")
        if min(self.initial_height_m,self.hill_height_m,self.final_height_m)<0:raise PhysicsValidationError("Track heights cannot be negative.")
        if self.initial_speed_m_s<0 or self.loss_per_meter_j<0:raise PhysicsValidationError("Initial speed and dissipative loss cannot be negative.")
        if not 3<=self.samples<=2000:raise PhysicsValidationError("Samples must be between 3 and 2000.")
    def to_dict(self):return {k:getattr(self,k) for k in self.__dataclass_fields__}
@dataclass(frozen=True,slots=True)
class RollerCoasterResult:
    parameters:RollerCoasterParameters;distance_m:tuple[float,...];height_m:tuple[float,...];speed_m_s:tuple[float,...];potential_energy_j:tuple[float,...];kinetic_energy_j:tuple[float,...];mechanical_energy_j:tuple[float,...];completed:bool;stopping_distance_m:float|None;energy_lost_j:float;maximum_speed_m_s:float;outcome:str
def _height(p,x):
    half=p.track_length_m/2
    return p.initial_height_m+(p.hill_height_m-p.initial_height_m)*x/half if x<=half else p.hill_height_m+(p.final_height_m-p.hill_height_m)*(x-half)/half
def simulate(p:RollerCoasterParameters)->RollerCoasterResult:
    p.validate();initial=p.mass_kg*p.gravity_m_s2*p.initial_height_m+.5*p.mass_kg*p.initial_speed_m_s**2;distance=[];height=[];speed=[];pe=[];ke=[];total=[];stop=None
    for i in range(p.samples):
        x=p.track_length_m*i/(p.samples-1);h=_height(p,x);available=initial-p.loss_per_meter_j*x-p.mass_kg*p.gravity_m_s2*h
        if available < -1e-8:
            stop=x;break
        available=max(0.,available);distance.append(x);height.append(h);pe.append(p.mass_kg*p.gravity_m_s2*h);ke.append(available);speed.append(math.sqrt(2*available/p.mass_kg));total.append(pe[-1]+ke[-1])
    completed=stop is None;lost=p.loss_per_meter_j*(distance[-1] if distance else 0);maximum=max(speed,default=0.)
    outcome=f"The coaster completes the track and reaches {maximum:.2f} m/s." if completed else f"The coaster cannot reach the next track point and stops near {stop:.1f} m."
    return RollerCoasterResult(p,tuple(distance),tuple(height),tuple(speed),tuple(pe),tuple(ke),tuple(total),completed,stop,lost,maximum,outcome)
