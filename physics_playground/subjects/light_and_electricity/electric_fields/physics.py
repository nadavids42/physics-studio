"""Pure bounded-grid electrostatics model with singularity safeguards."""
from dataclasses import dataclass
import math
from physics_playground.validation import PhysicsValidationError
COULOMB_CONSTANT=8.9875517923e9;MAX_FIELD_POINTS=2401;MAX_CHARGES=6
@dataclass(frozen=True,slots=True)
class PointCharge:
    charge_c:float;x_m:float;y_m:float
    def validate(self):
        if not all(math.isfinite(v) for v in (self.charge_c,self.x_m,self.y_m)):raise PhysicsValidationError("Charge values and positions must be finite.")
        if self.charge_c==0:raise PhysicsValidationError("Each source charge must be nonzero.")
    def to_dict(self):return {"charge_c":self.charge_c,"x_m":self.x_m,"y_m":self.y_m}
@dataclass(frozen=True,slots=True)
class ElectricFieldParameters:
    charges:tuple[PointCharge,...]=(PointCharge(1e-6,-1,0),PointCharge(-1e-6,1,0));test_charge_c:float=1e-9;test_x_m:float=0.;test_y_m:float=1.;extent_m:float=4.;grid_size:int=25;minimum_distance_m:float=.12
    def validate(self):
        if not 1<=len(self.charges)<=MAX_CHARGES:raise PhysicsValidationError(f"Use between one and {MAX_CHARGES} point charges.")
        for charge in self.charges:charge.validate()
        if not all(math.isfinite(v) for v in (self.test_charge_c,self.test_x_m,self.test_y_m,self.extent_m,self.minimum_distance_m)):raise PhysicsValidationError("Field parameters must be finite.")
        if self.extent_m<=0 or self.minimum_distance_m<=0:raise PhysicsValidationError("Field extent and minimum distance must be greater than zero.")
        if not 9<=self.grid_size<=49 or self.grid_size**2>MAX_FIELD_POINTS:raise PhysicsValidationError(f"Grid size must be 9–49 and no more than {MAX_FIELD_POINTS} total points.")
        for charge in self.charges:
            if math.hypot(self.test_x_m-charge.x_m,self.test_y_m-charge.y_m)<self.minimum_distance_m:raise PhysicsValidationError("Move the test charge farther from every source charge to avoid the point-charge singularity.")
    def to_dict(self):return {"charges":[c.to_dict() for c in self.charges],"test_charge_c":self.test_charge_c,"test_x_m":self.test_x_m,"test_y_m":self.test_y_m,"extent_m":self.extent_m,"grid_size":self.grid_size,"minimum_distance_m":self.minimum_distance_m}
@dataclass(frozen=True,slots=True)
class FieldSample:
    x_m:float;y_m:float;electric_x_n_c:float|None;electric_y_n_c:float|None;potential_v:float|None
@dataclass(frozen=True,slots=True)
class ElectricFieldResult:
    parameters:ElectricFieldParameters;samples:tuple[FieldSample,...];test_field_x_n_c:float;test_field_y_n_c:float;test_field_magnitude_n_c:float;test_potential_v:float;force_x_n:float;force_y_n:float;force_magnitude_n:float;excluded_points:int;outcome:str
def field_at(charges:tuple[PointCharge,...],x:float,y:float,minimum_distance:float)->tuple[float,float,float]:
    ex=ey=v=0.
    for charge in charges:
        dx=x-charge.x_m;dy=y-charge.y_m;r=math.hypot(dx,dy)
        if r<minimum_distance:raise PhysicsValidationError("Evaluation point is too close to a point-charge singularity.")
        ex+=COULOMB_CONSTANT*charge.charge_c*dx/r**3;ey+=COULOMB_CONSTANT*charge.charge_c*dy/r**3;v+=COULOMB_CONSTANT*charge.charge_c/r
    return ex,ey,v
def simulate(p:ElectricFieldParameters)->ElectricFieldResult:
    p.validate();samples=[];excluded=0
    for row in range(p.grid_size):
        y=-p.extent_m+2*p.extent_m*row/(p.grid_size-1)
        for column in range(p.grid_size):
            x=-p.extent_m+2*p.extent_m*column/(p.grid_size-1)
            try:ex,ey,v=field_at(p.charges,x,y,p.minimum_distance_m);samples.append(FieldSample(x,y,ex,ey,v))
            except PhysicsValidationError:samples.append(FieldSample(x,y,None,None,None));excluded+=1
    ex,ey,v=field_at(p.charges,p.test_x_m,p.test_y_m,p.minimum_distance_m);magnitude=math.hypot(ex,ey);fx=p.test_charge_c*ex;fy=p.test_charge_c*ey;force=math.hypot(fx,fy);direction="with" if p.test_charge_c>0 else ("opposite" if p.test_charge_c<0 else "unaffected by")
    return ElectricFieldResult(p,tuple(samples),ex,ey,magnitude,v,fx,fy,force,excluded,f"At the test point the field is {magnitude:.3g} N/C; the test charge feels {force:.3g} N {direction} the field direction. {excluded} grid points were excluded near singularities.")
