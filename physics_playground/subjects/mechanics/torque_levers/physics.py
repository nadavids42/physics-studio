"""Pure static lever and torque calculations."""
from dataclasses import dataclass
from physics_playground.subjects.mechanics.common import moment,require_finite
from physics_playground.validation import PhysicsValidationError
@dataclass(frozen=True,slots=True)
class LeverParameters:
    load_force_n:float=200.0;load_arm_m:float=.5;effort_force_n:float=80.0;effort_arm_m:float=1.5
    def validate(self):
        require_finite(load_force_n=self.load_force_n,load_arm_m=self.load_arm_m,effort_force_n=self.effort_force_n,effort_arm_m=self.effort_arm_m)
        if self.load_force_n<0 or self.effort_force_n<0:raise PhysicsValidationError("Forces cannot be negative.")
        if self.load_arm_m<=0 or self.effort_arm_m<=0:raise PhysicsValidationError("Lever arms must be greater than zero.")
    def to_dict(self):return {name:getattr(self,name) for name in self.__dataclass_fields__}
@dataclass(frozen=True,slots=True)
class LeverResult:
    parameters:LeverParameters;load_torque_n_m:float;effort_torque_n_m:float;net_torque_n_m:float;required_balance_force_n:float;mechanical_advantage:float;outcome:str
def simulate(p:LeverParameters)->LeverResult:
    p.validate();load=moment(p.load_force_n,p.load_arm_m);effort=moment(p.effort_force_n,p.effort_arm_m);net=effort-load;required=load/p.effort_arm_m;ma=p.effort_arm_m/p.load_arm_m
    outcome="The lever balances." if abs(net)<1e-9 else ("The effort side rotates downward." if net>0 else "The load side rotates downward.")
    return LeverResult(p,load,effort,net,required,ma,outcome)
