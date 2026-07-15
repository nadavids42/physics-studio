"""Pure tunnel-through-a-planet models."""
from __future__ import annotations
from dataclasses import asdict,dataclass
from enum import StrEnum
import math
import numpy as np
from physics_playground.contracts import AnimationData,AnimationKind,AnimationTrack,ContractResult,EventKind,ModelAssumption,PlotData,PlotSeries,SimulationEvent,SummaryMetric
from physics_playground.serialization import to_jsonable
from physics_playground.validation import PhysicsValidationError,require_positive
from physics_playground.performance import MAX_TRAJECTORY_SAMPLES,enforce_budget,validate_finite_parameters

class TunnelModel(StrEnum):UNIFORM="Uniform-density planet";RADIAL="Radial-density profile"
@dataclass(frozen=True,slots=True)
class TunnelParameters:
    radius_m:float
    surface_gravity_m_s2:float
    start_fraction:float=1.0
    model:TunnelModel=TunnelModel.UNIFORM
    density_gradient:float=.75
    samples:int=1000
    def validate(self):
        validate_finite_parameters(self)
        require_positive("Planet radius",self.radius_m);require_positive("Surface gravity",self.surface_gravity_m_s2)
        if not 0<self.start_fraction<=1:raise PhysicsValidationError("Starting depth fraction must be greater than 0 and at most 1.")
        if not 0<=self.density_gradient<1:raise PhysicsValidationError("Density gradient must be between 0 and 1.")
        if self.samples<10:raise PhysicsValidationError("Samples must be at least 10.")
        enforce_budget("Tunnel samples",self.samples,MAX_TRAJECTORY_SAMPLES)
    @property
    def uniform_period_s(self):return 2*math.pi*math.sqrt(self.radius_m/self.surface_gravity_m_s2)
    @property
    def mean_density_proxy(self):return self.surface_gravity_m_s2/self.radius_m
    def to_dict(self):
        d=to_jsonable(asdict(self));d["model"]=self.model.value;return d
@dataclass(frozen=True,slots=True)
class TunnelResult(ContractResult[TunnelParameters]):
    period_s:float=0.0
    opposite_time_s:float=0.0
    center_time_s:float=0.0
    maximum_speed_m_s:float=0.0
    energy_drift_fraction:float=0.0

def uniform_acceleration(position_m:float,p:TunnelParameters)->float:return -p.surface_gravity_m_s2*position_m/p.radius_m
def radial_acceleration(position_m:float,p:TunnelParameters)->float:
    if position_m==0:return 0.0
    x=min(1.0,abs(position_m)/p.radius_m);a=p.density_gradient;normal=1/3-a/4
    magnitude=p.surface_gravity_m_s2*(x/3-a*x*x/4)/normal
    return -math.copysign(magnitude,position_m)
def potential(position,p):
    x=np.abs(position)/p.radius_m
    if p.model==TunnelModel.UNIFORM:return .5*(p.surface_gravity_m_s2/p.radius_m)*position**2
    a=p.density_gradient;normal=1/3-a/4;return p.surface_gravity_m_s2*p.radius_m*(x*x/6-a*x**3/12)/normal
def _result(p,t,x,v,acc,period,method):
    energy=.5*v*v+potential(x,p);e0=max(abs(float(energy[0])),1e-12);drift=float(np.max(np.abs(energy-energy[0]))/e0);center=period/4
    return TunnelResult(simulation_id="earth_tunnel",parameters=p,metrics=(SummaryMetric("period","Full oscillation period",period,"s",f"{period/60:.1f} min"),SummaryMetric("opposite_time","Time to opposite turning point",period/2,"s",f"{period/120:.1f} min"),SummaryMetric("center_time","Time to center",center,"s",f"{center/60:.1f} min"),SummaryMetric("maximum_speed","Maximum speed",float(np.max(np.abs(v))),"m/s",f"{np.max(np.abs(v))/1000:.2f} km/s"),SummaryMetric("energy_drift","Energy drift",drift*100,"%",f"{drift*100:.5f}%")),
        events=(SimulationEvent("jump",EventKind.START,0,"Fall begins"),SimulationEvent("center",EventKind.MILESTONE,center,"Passes through the center"),SimulationEvent("opposite",EventKind.COMPLETION,period/2,"Reaches the opposite turning point")),
        plots=(PlotData("position_time","Position versus time","Time (minutes)","Position (km)",(PlotSeries("position",method,tuple(t/60),tuple(x/1000)),)),PlotData("velocity_time","Velocity versus time","Time (minutes)","Velocity (km/s)",(PlotSeries("velocity","v(t)",tuple(t/60),tuple(v/1000)),)),PlotData("acceleration_position","Acceleration versus position","Position (km)","Acceleration (m/s²)",(PlotSeries("acceleration","a(x)",tuple(x/1000),tuple(acc)),)),PlotData("energy_time","Specific energy versus time","Time (minutes)","Energy (J/kg)",(PlotSeries("energy","E(t)",tuple(t/60),tuple(energy)),))),
        animation=AnimationData(AnimationKind.ONE_DIMENSIONAL,tuple(t),(AnimationTrack("traveler","Traveler",tuple(x/1000),style={"color":"#FF7043"}),),4500,{"minimum":-p.radius_m/1000,"maximum":p.radius_m/1000}),
        assumptions=(ModelAssumption("spherical","The planet is perfectly spherical."),ModelAssumption("vacuum","The tunnel contains no air."),ModelAssumption("no_rotation","Planetary rotation is ignored.")),period_s=period,opposite_time_s=period/2,center_time_s=center,maximum_speed_m_s=float(np.max(np.abs(v))),energy_drift_fraction=drift)
def simulate_uniform(p:TunnelParameters)->TunnelResult:
    p.validate();period=p.uniform_period_s;omega=math.sqrt(p.surface_gravity_m_s2/p.radius_m);t=np.linspace(0,period*1.05,p.samples);amp=p.radius_m*p.start_fraction;x=amp*np.cos(omega*t);v=-amp*omega*np.sin(omega*t);acc=-omega**2*x
    return _result(p,t,x,v,acc,period,"Uniform-density analytic SHM")
def simulate_radial(p:TunnelParameters)->TunnelResult:
    p.validate();base=p.uniform_period_s;duration=base*1.6;t=np.linspace(0,duration,p.samples);dt=t[1]-t[0];s=np.zeros((p.samples,2));s[0]=(p.radius_m*p.start_fraction,0)
    def rhs(q):return np.array((q[1],radial_acceleration(q[0],p)))
    for i in range(1,p.samples):
        q=s[i-1];k1=rhs(q);k2=rhs(q+dt*k1/2);k3=rhs(q+dt*k2/2);k4=rhs(q+dt*k3);s[i]=q+dt*(k1+2*k2+2*k3+k4)/6
    crossings=np.where(np.signbit(s[:-1,0])!=np.signbit(s[1:,0]))[0]
    if not len(crossings):raise PhysicsValidationError("The radial-density integration did not reach the center; increase resolution.")
    i=crossings[0];fraction=s[i,0]/(s[i,0]-s[i+1,0]);center=t[i]+fraction*dt;period=4*center;keep=t<=period*1.05
    x=s[keep,0];v=s[keep,1];tt=t[keep];acc=np.array([radial_acceleration(value,p) for value in x]);return _result(p,tt,x,v,acc,period,"Radial-density RK4")
def simulate_tunnel(p:TunnelParameters)->TunnelResult:return simulate_uniform(p) if p.model==TunnelModel.UNIFORM else simulate_radial(p)
